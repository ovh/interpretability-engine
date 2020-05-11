#!/bin/bash

pip3 install . || exit 1

test_model(){
  local model="$1"
  local features="$2"
  local method="$3"

  echo "Try model ${model}"

  cp -r /app/misc/integration-tests/model-${model} /deployments/models

  nohup /deployments/run-java.sh >/app/nohup.out &2>1 || exit 10 &

  sleep 3s

  cat /app/nohup.out | grep -v "Exception" || exit 20

  interpretability-engine --token xxx --deployment-url http://localhost:8080 \
  --method ${method} \
  --samples-path /app/misc/integration-tests/${model}.csv \
  --features ${features} --output-file /tmp/result.pdf --log-level=DEBUG 2>&1 || exit 30

  ls /tmp/result.pdf || exit 50

  killall java >/dev/null || exit 60

  ps | grep -v java >/dev/null || exit 80

  rm -rf /deployments/models

  sleep 1s
}

test_model "iris" "0" "pdp"

test_model "boston" "CRIM ZN" "pdp"

# NOTE inspired from https://www.kaggle.com/secareanualin/football-events/data
test_model "multi-inputs" "event_type assist_method" "pdp"
