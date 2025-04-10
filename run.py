import uvicorn
import os

if __name__ == "__main__":
    mode = os.getenv("ENV")

    config = {
      "dev": {
        "reload": True,
        "host": "localhost",
        "log_level": "debug",
      },
      "prod": {
        "reload": False,
        "host": "0.0.0.0",
        "log_level": "info",
      },
    }
    mode_config = config[mode]
    uvicorn.run("app:app", port=8000, **mode_config)