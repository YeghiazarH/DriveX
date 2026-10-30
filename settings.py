"""Shared display, road, and gameplay settings."""

# 900 x 1956 matches the iPhone 16 display's 402:874 aspect ratio at a
# higher logical resolution; Viewport scales it to the actual browser window.
LOGICAL_WIDTH = 900
LOGICAL_HEIGHT = 1956
FPS = 60

ROAD_LEFT = LOGICAL_WIDTH * 0.11
ROAD_RIGHT = LOGICAL_WIDTH * 0.89
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_COUNT = 3
LANE_WIDTH = ROAD_WIDTH / LANE_COUNT
LANE_CENTERS = tuple(
    ROAD_LEFT + LANE_WIDTH * (lane + 0.5) for lane in range(LANE_COUNT)
)

GRASS = (48, 91, 61)
GRASS_DARK = (39, 75, 51)
ROAD = (48, 52, 57)
ROAD_EDGE = (208, 205, 190)
LANE_MARKER = (232, 228, 206)
PLAYER_GREEN = (28, 177, 105)
TRAFFIC_RED = (198, 53, 49)
WHITE = (255, 255, 255)
INK = (24, 29, 34)

PLAYER_Y = LOGICAL_HEIGHT * 0.67
MIN_SPEED = 150.0
MAX_SPEED = 390.0
START_SPEED = 210.0
ACCELERATION_STEP = 38.0
BRAKE_STEP = 55.0

TRAFFIC_WIDTH = ROAD_WIDTH * 0.23
TRAFFIC_HEIGHT = TRAFFIC_WIDTH * 1.72
LANE_DASH_LENGTH = LOGICAL_WIDTH * 0.065
LANE_DASH_GAP = LOGICAL_WIDTH * 0.085
HORIZON_Y = LOGICAL_HEIGHT * 0.16
ACTION_BUTTON_RECT = (
    LOGICAL_WIDTH * 0.22,
    LOGICAL_HEIGHT * 0.65,
    LOGICAL_WIDTH * 0.56,
    LOGICAL_HEIGHT * 0.09,
)


def road_progress_at(y):
    return max(0.0, min(1.0, (y - HORIZON_Y) / (LOGICAL_HEIGHT - HORIZON_Y)))


def road_bounds_at(y):
    progress = road_progress_at(y)
    width = ROAD_WIDTH * (0.66 + progress * 0.34)
    center = LOGICAL_WIDTH / 2
    return center - width / 2, center + width / 2, progress


def lane_center_at(lane, y):
    left, right, _ = road_bounds_at(y)
    return left + (right - left) * (lane + 0.5) / LANE_COUNT


def vehicle_scale_at(y):
    return 0.52 + road_progress_at(y) * 0.48


PLAYER_WIDTH = TRAFFIC_WIDTH * vehicle_scale_at(PLAYER_Y)
PLAYER_HEIGHT = TRAFFIC_HEIGHT * vehicle_scale_at(PLAYER_Y)
