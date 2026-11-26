#!/bin/sh
# The service against a stand-in for Gemini (tests/fake_gemini.py): streaming, the memory of the chat, the model picker,
# the errors, the feedback, clearing, the key of the server, and the offline stand-in. Run from telvax/: sh tests/e2e.sh
set -eu
TELVAX=${TELVAX:-telvax}
dir=$(mktemp -d)
pids=""
trap 'for p in $pids; do kill "$p" 2>/dev/null || true; done; rm -rf "$dir"' EXIT
fail() { echo "FAIL: $*"; exit 1; }

python3 tests/fake_gemini.py 18831 "$dir/fake.log" & pids="$pids $!"
GEMINI_BASE_URL=http://127.0.0.1:18831/ "$TELVAX" serve src/main.tvx --live --port 18830 > "$dir/a.log" 2>&1 & pids="$pids $!"
GOOGLE_API_KEY=serverkey GEMINI_BASE_URL=http://127.0.0.1:18831/ "$TELVAX" serve src/main.tvx --live --port 18832 > "$dir/b.log" 2>&1 & pids="$pids $!"
"$TELVAX" serve src/main.tvx --port 18833 > "$dir/c.log" 2>&1 & pids="$pids $!"
for port in 18830 18832 18833; do
  for i in $(seq 1 50); do curl -fs "localhost:$port/healthz" > /dev/null && break; sleep 0.2; done
done

J="$dir/jar"
chat() { curl -s -b "$J" -c "$J" -X POST "localhost:${2:-18830}/api/chat" -H 'content-type: application/json' -d "$1"; }
last() { tail -n 1 "$dir/fake.log"; }

curl -s -c "$J" -o "$dir/page.html" localhost:18830/
grep -q "Gemini Chatbot" "$dir/page.html" || fail "the page"

out=$(chat '{"message":"Olá","model":"gemini-3.8-flash","api_key":"k1"}')
echo "$out" | grep -q '^data: {"text":"Resposta"}' || fail "streamed pieces: $out"
echo "$out" | grep -q 'event: done' || fail "done: $out"
out=$(chat '{"message":"E depois?","model":"gemini-3.8-flash","api_key":"k1"}')
last | grep -q '"stream": true' || fail "a streamed request"
last | grep -q 'assistant' || fail "the history goes back to the model: $(last)"
echo "$out" | grep -q '{"text":" 2"}' || fail "second turn: $out"

chat '{"message":"Outro modelo","model":"gemini-2.5-flash","api_key":"k1"}' > /dev/null
last | grep -q '"model": "gemini-2.5-flash"' || fail "the model picker"
[ "$(last | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["messages"]))')" = 1 ] || fail "a new model starts a new chat session"

chat '{"message":"x","model":"gemini-3.8-flash","api_key":"bad"}' | grep -q 'Chave de API inválida' || fail "bad key"
chat '{"message":"x","model":"gemini-2.5-pro","api_key":"k1"}' | grep -q 'Modelo indisponível' || fail "404"
chat '{"message":"x","model":"gemini-3.8-flash","api_key":"quota"}' | grep -q 'Cota da API excedida' || fail "429"
chat '{"message":"x","model":"gemini-3.8-flash"}' | grep -q 'Adicione sua Google API Key' || fail "no key"

curl -s -b "$J" -X POST localhost:18830/api/feedback -H 'content-type: application/json' -d '{"index":1,"rating":"Útil"}' | grep -q '"rating":"Útil"' || fail "feedback"
curl -s -b "$J" -X POST localhost:18830/api/feedback -H 'content-type: application/json' -d '{"index":0,"rating":"Útil"}' | grep -q 'only an answer' || fail "feedback on a user message"
curl -s -b "$J" localhost:18830/api/state | grep -q '"rating":"Útil"' || fail "the rating in the state"
curl -s -b "$J" -X DELETE localhost:18830/api/chat | grep -q 'Conversa reiniciada' || fail "clear"
curl -s -b "$J" localhost:18830/api/state | grep -q '"messages":\[\]' || fail "cleared state"

curl -s localhost:18832/api/state | grep -q '"server_key":true' || fail "server key flag"
chat '{"message":"Oi","api_key":"ignored"}' 18832 > /dev/null
last | grep -q '"key": "serverkey"' || fail "the key of the server is used"

curl -s -X POST localhost:18833/api/chat -H 'content-type: application/json' -d '{"message":"Oi","api_key":"k"}' | grep -q 'event: done' || fail "offline stand-in"
echo "e2e: all checks passed"
