# algo-clustering-server
1. docker compose up for container run
1. make start for local run
1. make start-reload for local hotload run

# note for local run
1. run redis and mongo with docker compose
1. run celery and app with make command

# Docker run
1. Download the last 5 files in here (https://huggingface.co/vinai/phobert-base-v2/tree/main) to the model folder (create model folder in the root if not existed)
1. File list: [bpe.codes, config.json, pytorch_model.bin, tokenizer.json, vocab.txt]
1. Run docker compose