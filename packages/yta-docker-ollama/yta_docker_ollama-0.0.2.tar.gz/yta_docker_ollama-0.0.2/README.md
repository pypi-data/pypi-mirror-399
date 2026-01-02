# Youtube Autonomous Docker Ollama Module

A module based on docker to use Ollama and make AI models available through local endpoints.

---
Proyect created based on this post: https://dev.to/savvasstephnds/run-deepseek-locally-using-docker-2pdm. I've modified it a bit by installing a different model, as I used the `deepseek-r1:latest` instead of the `deepseek-r1:7b` (you can check the list here: https://www.ollama.com/library/deepseek-r1).

---

### Instructions
1. Install the docker container that includes `ollama`. This command will create a local `ollama-models` folder in which the models will be downloaded (~2.6GB).
```
docker compose up -d ollama
```

2. Check that the container has been succesfully installed and is running locally by accessing to the following url. A `Ollama is running` message should appear in the web navigator:
```
http://localhost:11434/
```

3. Install `Deepseek` to be used in the `Ollama` container we've installed before, that will be downloaded (~5.2GB):
```
docker compose exec ollama ollama pull deepseek-r1:latest
```

4. Request to the `http://localhost:11434/api/generate` endpoint (using a `POST` method and providing the model and the parameters needed to obtain a response).
```
payload = {
    'model': model.value,
    'prompt': prompt,
    'stream': False
}

response = requests.post(
    url = OLLAMA_GENERATE_URL,
    json = payload
)
```

### Other models
*To install any other model, look for it in the list mentioned on top of this readme file and install it with the same command as before. If you want to install the `llama3.2-vision:latest`, just execute this command below:
```
docker compose exec ollama ollama pull llama3.2-vision:latest
```