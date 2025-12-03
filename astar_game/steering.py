# ============================================================================
# steering.py
# Purpose
#   Implement all steering behaviours here. Each function computes a steering
#   force vector. Entities apply that force to their velocity each frame.
# Key idea
#   desired_velocity minus current_velocity gives the steering force.
#   Use dt in update loops when integrating velocity to keep motion consistent.
# ============================================================================

import math
import random

from pygame import Rect
from pygame.math import Vector2 as V2

from astar_game.config import (ARRIVE_BRAKE_BOOST, ARRIVE_SLOW_RADIUS,
                               ARRIVE_SNAP_GAIN, ARRIVE_STOP_RADIUS,
                               AVOID_ANGLE_INCREMENT, AVOID_LOOKAHEAD,
                               AVOID_MAX_ANGLE, FPS, PATH_LOOKAHEAD)
from astar_game.utils import (circlecast_hits_any_rect, limit,
                              segment_circlecast_hits_rect)

# ---------------- Base behaviours ----------------


def seek(pos, vel, target, max_speed):
    """
    Move toward a target. Returns a steering force.
    desired = direction_to_target * max_speed
    steering = desired - current_velocity
    """
    d = target - pos
    if d.length_squared() == 0:
        return V2()
    desired = d.normalize() * max_speed
    return desired - vel


def flee(pos, vel, target, max_speed):
    """
    Move away from a target. This is the opposite of seek.
    You need to implement the mirror of seek using direction from threat to self.
    """
    d = pos - target
    if d.length_squared() == 0:
        return V2()
    desired = d.normalize() * max_speed
    return desired - vel


def arrive(
    pos: V2,
    vel: V2,
    target: V2,
    max_speed: float,
    slow_radius=ARRIVE_SLOW_RADIUS,
    stop_radius=ARRIVE_STOP_RADIUS,
):
    """
    Like seek when far, but slow down near the target.
    Rules
      If distance < stop_radius, return a force that cancels leftover velocity
      If distance < slow_radius, scale desired speed by distance / slow_radius
      Otherwise use full speed
    Inside slow radius, adds a lateral snap force to pivot toward the new target
    and boosts braking when re-targeting nearby to prevent overshoot.
    Frame-rate independent: uses steering forces that work with dt in integrate_velocity.
    """
    to_target = target - pos
    distance = to_target.length()
    desired_vel = V2()

    # Handle case where target is at current position
    if distance < stop_radius:
        """
        Stop immediately by returning a large opposing force.
        This creates a strong braking force that works with dt integration.
        The magnitude is chosen to be large enough to stop quickly regardless of FPS.
        """
        return -vel * 10.0

    # Avoid division by zero or normalization of zero vector
    if distance < 0.001:
        return V2()

    if distance < slow_radius:
        speed_factor = distance / slow_radius
        desired_speed = max_speed * speed_factor
    else:
        desired_speed = max_speed

    desired_vel = to_target.normalize() * desired_speed

    steering = desired_vel - vel

    # Inside slow radius: add lateral snap to pivot faster when re-targeting
    if stop_radius < distance < slow_radius:
        desired_dir = to_target.normalize()
        lateral_vel = vel - desired_dir * vel.dot(desired_dir)
        if lateral_vel.length_squared():
            steering -= lateral_vel * ARRIVE_SNAP_GAIN

    return steering


def integrate_velocity(vel, force, dt, max_speed):
    """
    Apply a steering force to velocity using Euler integration.
    Then clamp to max speed and return the new velocity.
    Use this inside agent update methods after computing steering forces.
    """
    vel += limit(force, 800) * dt
    if vel.length() > max_speed:
        vel.scale_to_length(max_speed)
    return vel


def follow_path(pos, vel, path, lookahead=PATH_LOOKAHEAD, max_speed=200.0):
    """
    Path following behavior: projects position onto path and steers toward a lookahead point.

    Args:
        pos: Current position (V2)
        vel: Current velocity (V2)
        path: List of waypoints (V2) representing the path
        lookahead: Distance to look ahead along the path
        max_speed: Maximum speed for steering

    Returns:
        Steering force (V2) to follow the path
    """
    if not path or len(path) < 2:
        return V2()

    # Find the closest point on the path
    closest_point = None
    closest_dist_sq = float('inf')
    closest_segment_idx = 0

    # Check each segment of the path
    for i in range(len(path) - 1):
        segment_start = path[i]
        segment_end = path[i + 1]

        # Project position onto this segment
        segment_vec = segment_end - segment_start
        segment_len_sq = segment_vec.length_squared()

        if segment_len_sq < 0.001:
            # Degenerate segment, use endpoint
            dist_sq = (pos - segment_start).length_squared()
            if dist_sq < closest_dist_sq:
                closest_dist_sq = dist_sq
                closest_point = segment_start
                closest_segment_idx = i
        else:
            # Project onto segment
            t = (pos - segment_start).dot(segment_vec) / segment_len_sq
            t = max(0.0, min(1.0, t))  # Clamp to segment

            point_on_segment = segment_start + segment_vec * t
            dist_sq = (pos - point_on_segment).length_squared()

            if dist_sq < closest_dist_sq:
                closest_dist_sq = dist_sq
                closest_point = point_on_segment
                closest_segment_idx = i

    if closest_point is None:
        return V2()

    # Find the lookahead point along the path
    lookahead_point = None
    remaining_lookahead = lookahead

    # Start from the closest segment and move forward
    for i in range(closest_segment_idx, len(path) - 1):
        segment_start = path[i]
        segment_end = path[i + 1]
        segment_vec = segment_end - segment_start
        segment_len = segment_vec.length()

        if segment_len < 0.001:
            continue

        # Calculate how far along this segment we should go
        if i == closest_segment_idx:
            # Start from the closest point on this segment
            segment_start = closest_point

        segment_vec = segment_end - segment_start
        segment_len = segment_vec.length()

        if remaining_lookahead <= segment_len:
            # Lookahead point is on this segment
            t = remaining_lookahead / segment_len
            lookahead_point = segment_start + segment_vec * t
            break
        else:
            # Move past this segment
            remaining_lookahead -= segment_len

    # If we didn't find a lookahead point (reached end of path), use the last waypoint
    if lookahead_point is None:
        lookahead_point = path[-1]

    # Use arrive to move toward the lookahead point, slowing down when close
    return arrive(pos, vel, lookahead_point, max_speed)

# ---------------- Obstacle avoidance blend ----------------


def seek_with_avoid(pos, vel, target, max_speed, radius, rects: list[Rect], lookahead=AVOID_LOOKAHEAD, debug_info=None) -> V2:
    """
    Seek the target but avoid obstacles by sampling angled corridors.
    Idea
      1. Check a straight corridor first
      2. If blocked, rotate small angles left and right until a free path is found
      3. Use that direction for the seek
      4. If all blocked, apply a small braking force
    Use circlecast_hits_any_rect to test each corridor.

    If debug_info dict is provided, it will be populated with visualization data:
      - base_direction: V2, normalized direction to target
      - tested_angles: list of tuples (angle_deg, direction, endpoint, is_free)
      - selected_direction: V2 or None, the chosen free direction
      - lookahead: float, the lookahead distance used
    """
    circlecast_hits_any_rect_step = 8.0
    # Calculate base direction to target
    to_target = target - pos
    if to_target.length_squared() == 0:
        if debug_info is not None:
            debug_info['base_direction'] = V2()
            debug_info['tested_angles'] = []
            debug_info['selected_direction'] = None
            debug_info['lookahead'] = lookahead
        return V2()

    base_direction = to_target.normalize()

    # Initialize debug info if requested
    if debug_info is not None:
        debug_info['base_direction'] = base_direction
        debug_info['tested_angles'] = []
        debug_info['selected_direction'] = None
        debug_info['lookahead'] = lookahead

    # Test straight corridor first (0 degrees)
    p1_straight = pos + base_direction * lookahead
    straight_free = not circlecast_hits_any_rect(
        pos, p1_straight, radius, rects, step=circlecast_hits_any_rect_step)

    if debug_info is not None:
        debug_info['tested_angles'].append(
            (0.0, base_direction, p1_straight, straight_free))

    if straight_free:
        # Straight path is clear, use normal seek
        if debug_info is not None:
            debug_info['selected_direction'] = base_direction
        return seek(pos, vel, target, max_speed)

    max_steps = math.ceil(AVOID_MAX_ANGLE / AVOID_ANGLE_INCREMENT)
    free_direction = None

    for step in range(1, max_steps + 1):
        angle_deg = step * AVOID_ANGLE_INCREMENT

        # Test left rotation (negative angle)
        left_direction = base_direction.rotate(-angle_deg)
        p1_left = pos + left_direction * lookahead
        left_free = not circlecast_hits_any_rect(
            pos, p1_left, radius, rects, step=circlecast_hits_any_rect_step)

        if debug_info is not None:
            debug_info['tested_angles'].append(
                (-angle_deg, left_direction, p1_left, left_free))

        if left_free:
            free_direction = left_direction
            if debug_info is not None:
                debug_info['selected_direction'] = free_direction
            break

        # Test right rotation (positive angle)
        right_direction = base_direction.rotate(angle_deg)
        p1_right = pos + right_direction * lookahead
        right_free = not circlecast_hits_any_rect(
            pos, p1_right, radius, rects, step=circlecast_hits_any_rect_step)

        if debug_info is not None:
            debug_info['tested_angles'].append(
                (angle_deg, right_direction, p1_right, right_free))

        if right_free:
            free_direction = right_direction
            if debug_info is not None:
                debug_info['selected_direction'] = free_direction
            break

    if free_direction is not None:
        desired = free_direction * (max_speed * FPS)
        return desired - vel

    for rect in rects:
        if segment_circlecast_hits_rect(pos, pos + base_direction * lookahead, radius, rect, step):
            direction = (pos - rect.center).normalize()
            desired = direction * (max_speed * FPS)
            if debug_info is not None:
                debug_info['selected_direction'] = direction
            return desired - vel

    # if no case match, travel in reverse -> avoid crash
    return -vel * 2
