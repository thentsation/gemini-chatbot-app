"""A stand-in for Gemini's OpenAI-compatible endpoint, for the end-to-end test of the Telvax service.

It answers `POST /chat/completions` (streamed when asked), writes every request to the file of its second argument as
one JSON line (the model, the messages, the key it got), and fails the way Gemini does: key `bad` gives 401, model
`gemini-2.5-pro` 404, key `quota` 429.
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

port, log = int(sys.argv[1]), sys.argv[2]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def answer(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('content-type', 'application/json')
        self.send_header('content-length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['content-length'])))
        key = self.headers.get('authorization', '').removeprefix('Bearer ')
        with open(log, 'a') as f:
            f.write(json.dumps({'model': body['model'], 'messages': body['messages'], 'key': key, 'stream': body.get('stream', False)}) + '\n')
        if key == 'bad':
            return self.answer(401, {'error': {'code': 401, 'message': 'API key not valid.', 'status': 'UNAUTHENTICATED'}})
        if key == 'quota':
            return self.answer(429, {'error': {'code': 429, 'message': 'Resource exhausted.', 'status': 'RESOURCE_EXHAUSTED'}})
        if body['model'] == 'gemini-2.5-pro':
            return self.answer(404, {'error': {'code': 404, 'message': 'models/gemini-2.5-pro is not found.', 'status': 'NOT_FOUND'}})
        last = body['messages'][-1]['content']
        turns = len(body['messages'])
        words = f'Resposta {turns // 2 + 1} a "{last}" com {body["model"]}.'.split(' ')
        if not body.get('stream'):
            return self.answer(200, {'choices': [{'message': {'role': 'assistant', 'content': ' '.join(words)}, 'finish_reason': 'stop'}],
                                     'usage': {'prompt_tokens': turns, 'completion_tokens': len(words)}})
        self.send_response(200)
        self.send_header('content-type', 'text/event-stream')
        self.end_headers()
        for i, w in enumerate(words):
            piece = w if i == 0 else ' ' + w
            chunk = {'choices': [{'delta': {'content': piece}, 'finish_reason': None}]}
            self.wfile.write(f'data: {json.dumps(chunk)}\n\n'.encode())
            self.wfile.flush()
        end = {'choices': [{'delta': {}, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': turns, 'completion_tokens': len(words)}}
        self.wfile.write(f'data: {json.dumps(end)}\n\ndata: [DONE]\n\n'.encode())


ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
