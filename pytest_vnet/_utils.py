#!/usr/bin/env python3

from typing import Tuple


class NonZeroExitcode(Exception):
	pass


def stream_run(cont, *args, **kwargs):

	"""Run and stream output of exec run on container, first argument is that container,
	takes same arguments as docker py container `exec_run`, except for `stream` that is always
	`True`.
	"""
	_, out = cont.exec_run(
		stream=True, *args, **kwargs
	)

	all_out = ""
	for chunk in out:
		text = chunk.decode("utf-8")
		print(text, end="", flush=True)
		all_out += text


def background_run(cont, *args, **kwargs) -> int:
	"""Run and if a non zero exit code is returned raise exception
	"""
	print(" ".join(args[0]), end="...", flush=True)
	ec, _ = cont.exec_run(
		*args, **kwargs
	)
	if ec != 0:
		print("exception!")
		raise NonZeroExitcode(
			f"Command \"{args[0]}\" returned non zero exitcode {ec}."
		)
	print("done!")