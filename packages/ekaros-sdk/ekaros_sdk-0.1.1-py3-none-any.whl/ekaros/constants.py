EKAROS_DOMAIN = 0
API_TIMEOUT = 30

EKAROS_API_ENDPOINT = "http://localhost:8002"
EKAROS_LOGIC_API_ENDPOINT = "http://localhost:8008"

CLIENT_SDK_TOKEN_CREATE_END_POINT = EKAROS_API_ENDPOINT + "/v1/project/client/sdk/key/create/"
SERVER_SDK_INIT_END_POINT = EKAROS_API_ENDPOINT + "/v1/project/server/sdk/init/"
SERVER_SDK_KEY_VALIDATION_END_POINT = EKAROS_API_ENDPOINT + "/v1/project/server/sdk/validate/"
REGISTER_SERVER_VIEWS_END_POINT = EKAROS_LOGIC_API_ENDPOINT + "/v1/project/register/server/view/"
GET_ALL_JOURNIES = EKAROS_LOGIC_API_ENDPOINT + "/v1/project/journey/backend/all/?domain={domain}"

# Server Registration
SERVER_REGISTRATION_END_POINT = f"{EKAROS_LOGIC_API_ENDPOINT}/v1/sse/sdk/server/register/"
SERVER_HEARTBEAT_END_POINT = f"{EKAROS_LOGIC_API_ENDPOINT}/v1/sse/sdk/server/heartbeat/"
SERVER_DEREGISTRATION_END_POINT = f"{EKAROS_LOGIC_API_ENDPOINT}/v1/sse/sdk/server/deregister/"

# SSE Stream
SSE_STREAM_END_POINT = f"{EKAROS_LOGIC_API_ENDPOINT}/v1/sse/sdk/server/stream/journey-updates/"

# Polling Fallback
JOURNEY_POLLING_END_POINT = f"{EKAROS_LOGIC_API_ENDPOINT}/v1/sse/sdk/server/journey/poll/"
POLLING_INTERVAL = 30  # seconds
SSE_RECONNECT_DELAY = 5  # seconds
HEARTBEAT_INTERVAL = 10
SSE_SSL_VERIFICATION = False
SSE_TIMEOUT = 30
MEMORY_SAMPLING_RATE: float = 0.05

# Events
EKAROS_EVENTS_ENDPOINT = f"{EKAROS_LOGIC_API_ENDPOINT}/v1/project/events/backend/"
REQUEST_TIMEOUT_SECONDS = 3
