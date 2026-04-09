import uvicorn
from env.microgrid import MicrogridEnv
from openenv.core.env_server import create_app
from env.models import MicrogridState, MicrogridAction, StepRecord, StepResult, GradeResult

app = create_app(
    MicrogridEnv,
    action_type = MicrogridAction,
    observation_type=MicrogridState,
    env_name="microgrid_v1"
)

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()