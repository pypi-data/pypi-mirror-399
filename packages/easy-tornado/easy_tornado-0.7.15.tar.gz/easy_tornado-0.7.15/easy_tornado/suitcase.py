# -*- coding: utf-8 -*-
# author: 王树根
# email: wsg1107556314@163.com
# date: 2025/12/16 23:03


def add_criteria_argument(parser):
  parser.add_argument(
    '--criteria', '-c', action='append', default=[],
    help='criteria to eval, if not True then filter out, "obj" is the dict'
  )
  parser.add_argument(
    '--silent', '-s', action='store_true', default=False,
    help='silent mode for less output'
  )


def add_io_arguments(parser, multi_input=False):
  input_parser = parser.add_mutually_exclusive_group(required=True)
  input_parser.add_argument(
    '--mapreduce', '-mr', action='store_true', default=False,
    help='read and write in mapreduce procedure manner'
  )
  if multi_input:
    input_parser.add_argument(
      '--input-paths', '-i', action='append', default=[],
      help='paths to input file'
    )
  else:
    input_parser.add_argument(
      '--input-path', '-i', default=None,
      help='path to input file'
    )
  add_criteria_argument(parser)
  parser.add_argument(
    '--dry-run', '-dr', action='store_true', default=False,
    help='test data loader and do not execute'
  )
  parser.add_argument(
    '--json-pro', '-jp', action='store_true', default=False,
    help='use jsonlines to load lines instead of load_file_contents'
  )
  parser.add_argument(
    '--output-path', '-o', default=None,
    help='path to output results file'
  )
  parser.add_argument(
    '--remove-if-exists', '-rie', action='store_true', default=False,
    help='remove output path if already exists'
  )
  return input_parser


def add_qps_argument(parser):
  parser.add_argument(
    '--query-per-second', '-qps', type=int, default=2,
    help='request/invoke speed limit'
  )
  parser.add_argument(
    '--timeout', '-to', type=int, default=3600,
    help='request/invoke timeout seconds'
  )
  parser.add_argument(
    '--patience', '-rp', type=int, default=3,
    help='max retry times before give up'
  )


def add_ckpt_argument(parser):
  parser.add_argument(
    '--keep-as-key', '-kak', default=None,
    help='KEEP request/invoke result as an attribute'
  )
  parser.add_argument(
    '--write-interval', '-wi', type=int, default=10,
    help='save interval: per number of lines'
  )
