#!/usr/bin/env python3

def stream_run(cont, *args, **kwargs):
	ec, out = cont.exec_run(
		stream=True, *args, **kwargs
	)

	all_out = ""
	for chunk in out:
		text = chunk.decode("utf-8")
		print(text, end="", flush=True)
		all_out += text

	return (ec, all_out)