docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gaiaadm/pumba \
  netem \
  --duration {{DURATION}} \
  delay \
  --time {{LATENCY}} \
  {{CONTAINER}}