# -*- coding: utf-8 -*-
#
#      DVR-Scan: Video Motion Event Detection & Extraction Tool
#   --------------------------------------------------------------
#       [  Site: https://github.com/Breakthrough/DVR-Scan/   ]
#       [  Documentation: http://dvr-scan.readthedocs.org/   ]
#
# Copyright (C) 2014-2022 Brandon Castellano <http://www.bcastell.com>.
# PySceneDetect is licensed under the BSD 2-Clause License; see the
# included LICENSE file, or visit one of the above pages for details.
#
""" ``dvr_scan.cli`` Module

This module provides the get_cli_parser() function, which provides
an argparse-based CLI parser used by the DVR-Scan application.
"""

import argparse
from typing import List, Optional

import dvr_scan


def timecode_type_check(metavar: Optional[str] = None):
    """ Creates an argparse type for a user-inputted timecode.

    The passed argument is declared valid if it meets one of three valid forms:
      1) Standard timecode; in form HH:MM:SS or HH:MM:SS.nnn
      2) Number of seconds; type # of seconds, followed by s (e.g. 54s, 0.001s)
      3) Exact number of frames; type # of frames (e.g. 54, 1000)
     valid integer which
    is greater than or equal to min_val, and if max_val is specified,
    less than or equal to max_val.

    Returns:
        A function which can be passed as an argument type, when calling
        add_argument on an ArgumentParser object

    Raises:
        ArgumentTypeError: Passed argument must be integer within proper range.
    """
    metavar = 'value' if metavar is None else metavar

    def _type_checker(value):
        valid = False
        value = str(value).lower().strip()
        # Integer number of frames.
        if value.isdigit():
            # All characters in string are digits, just parse as integer.
            frames = int(value)
            if frames >= 0:
                valid = True
                value = frames
        # Integer or real/floating-point number of seconds.
        elif value.endswith('s'):
            secs = value[:-1]
            if secs.replace('.', '').isdigit():
                secs = float(secs)
                if secs >= 0.0:
                    valid = True
                    value = secs
        # Timecode in HH:MM:SS[.nnn] format.
        elif ':' in value:
            tc_val = value.split(':')
            if (len(tc_val) == 3 and tc_val[0].isdigit() and tc_val[1].isdigit()
                    and tc_val[2].replace('.', '').isdigit()):
                hrs, mins = int(tc_val[0]), int(tc_val[1])
                secs = float(tc_val[2]) if '.' in tc_val[2] else int(tc_val[2])
                if (hrs >= 0 and mins >= 0 and secs >= 0 and mins < 60 and secs < 60):
                    valid = True
                    value = [hrs, mins, secs]
        if not valid:
            raise argparse.ArgumentTypeError(
                'invalid timecode: %s\n'
                'Timecode must be specified as number of frames (12345), seconds (number followed'
                ' by s, e.g. 123s or 123.45s), or timecode (HH:MM:SS[.nnn].' % value)
        return value

    return _type_checker


def int_type_check(min_val: int, max_val: Optional[int] = None, metavar: Optional[str] = None):
    """ Creates an argparse type for a range-limited integer.

    The passed argument is declared valid if it is a valid integer which
    is greater than or equal to min_val, and if max_val is specified,
    less than or equal to max_val.

    Returns:
        A function which can be passed as an argument type, when calling
        add_argument on an ArgumentParser object

    Raises:
        ArgumentTypeError: Passed argument must be integer within proper range.
    """
    metavar = 'value' if metavar is None else metavar

    def _type_checker(value):
        value = int(value)
        valid = True
        msg = ''
        if max_val is None:
            if value < min_val:
                valid = False
            msg = 'invalid choice: %d (%s must be at least %d)' % (value, metavar, min_val)
        else:
            if value < min_val or value > max_val:
                valid = False
            msg = 'invalid choice: %d (%s must be between %d and %d)' % (value, metavar, min_val,
                                                                         max_val)
        if not valid:
            raise argparse.ArgumentTypeError(msg)
        return value

    return _type_checker


def odd_int_type_check(min_val: int,
                       max_val: Optional[int] = None,
                       metavar: Optional[str] = None,
                       allow_zero: bool = True):
    """ Creates an argparse type for a range-limited integer which must be odd.

    The passed argument is declared valid if it is a valid integer which is odd
    (i.e. the modulus of the value with respect to two is non-zero), is greater
    than or equal to min_val, and, if specified, less than or equal to max_val.

    Returns:
        A function which can be passed as an argument type, when calling
        add_argument on an ArgumentParser object

    Raises:
        ArgumentTypeError: Argument must be odd integer within specified range.
    """
    metavar = 'value' if metavar is None else metavar

    def _type_checker(value):
        value = int(value)
        valid = True
        msg = ''
        if value == -1:
            return -1
        if value == 0 and allow_zero is True:
            return 0
        if (value % 2) == 0:
            valid = False
            msg = 'invalid choice: %d (%s must be an odd number)' % (value, metavar)
        elif max_val is None:
            if value < min_val:
                valid = False
            msg = 'invalid choice: %d (%s must be at least %d)' % (value, metavar, min_val)
        else:
            if value < min_val or value > max_val:
                valid = False
            msg = 'invalid choice: %d (%s must be between %d and %d)' % (value, metavar, min_val,
                                                                         max_val)
        if not valid:
            raise argparse.ArgumentTypeError(msg)
        return value

    return _type_checker


def float_type_check(min_val: float,
                     max_val: Optional[float] = None,
                     metavar: Optional[str] = None,
                     default_str: Optional[str] = None):
    """ Creates an argparse type for a range-limited float.

    The passed argument is declared valid if it is a valid float which is
    greater thanmin_val, and if max_val is specified, less than max_val.

    Returns:
        A function which can be passed as an argument type, when calling
        add_argument on an ArgumentParser object

    Raises:
        ArgumentTypeError: Passed argument must be float within proper range.
    """
    metavar = 'value' if metavar is None else metavar

    def _type_checker(value):
        if default_str and isinstance(value, str) and default_str == value:
            return None
        value = float(value)
        valid = True
        msg = ''
        if max_val is None:
            if value < min_val:
                valid = False
            msg = 'invalid choice: %3.1f (%s must be greater than %3.1f)' % (value, metavar,
                                                                             min_val)
        else:
            if value < min_val or value > max_val:
                valid = False
            msg = 'invalid choice: %3.1f (%s must be between %3.1f and %3.1f)' % (value, metavar,
                                                                                  min_val, max_val)
        if not valid:
            raise argparse.ArgumentTypeError(msg)
        return value

    return _type_checker


def string_type_check(valid_strings: List[str],
                      case_sensitive: bool = True,
                      metavar: Optional[str] = None):
    """ Creates an argparse type for a list of strings.

    The passed argument is declared valid if it is a valid string which exists
    in the passed list valid_strings.  If case_sensitive is False, all input
    strings and strings in valid_strings are processed as lowercase.  Leading
    and trailing whitespace is ignored in all strings.

    Returns:
        A function which can be passed as an argument type, when calling
        add_argument on an ArgumentParser object

    Raises:
        ArgumentTypeError: Passed argument must be string within valid list.
    """
    metavar = 'value' if metavar is None else metavar
    valid_strings = [x.strip() for x in valid_strings]
    if not case_sensitive:
        valid_strings = [x.lower() for x in valid_strings]

    def _type_checker(value):
        value = str(value)
        valid = True
        if not case_sensitive:
            value = value.lower()
        if not value in valid_strings:
            valid = False
            case_msg = ' (case sensitive)' if case_sensitive else ''
            msg = 'invalid choice: %s (valid settings for %s%s are: %s)' % (
                value, metavar, case_msg, valid_strings.__str__()[1:-1])
        if not valid:
            raise argparse.ArgumentTypeError(msg)
        return value

    return _type_checker


# pylint: disable=too-few-public-methods
class AboutAction(argparse.Action):
    """Custom argparse action for displaying the DVR-Scan ABOUT_STRING.

    Based off of the default VersionAction for displaying a string to the user.
    """

    # pylint: disable=redefined-builtin, too-many-arguments
    def __init__(self,
                 option_strings,
                 version=None,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help="show version number and license/copyright information"):
        super(AboutAction, self).__init__(
            option_strings=option_strings, dest=dest, default=default, nargs=0, help=help)
        self.version = version

    def __call__(self, parser, namespace, values, option_string=None):
        version = self.version
        if version is None:
            version = parser.version
        parser.exit(message=version)


def get_cli_parser():
    """Creates the DVR-Scan argparse command-line interface.

    Returns:
        ArgumentParser object, which parse_args() can be called with.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # pylint: disable=protected-access
    parser._optionals.title = 'arguments'

    parser.add_argument('-v', '--version', action=AboutAction, version=dvr_scan.ABOUT_STRING)

    parser.add_argument(
        '-i',
        '--input',
        metavar='VIDEO_FILE',
        required=True,
        type=str,
        action='append',
        help=('[REQUIRED] Path to input video. May be specified multiple'
              ' times to join several videos with the same resolution'
              ' and framerate. Any output filenames will be generated'
              ' using the first filename only.'))

    parser.add_argument(
        '-o',
        '--output',
        metavar='OUTPUT_VIDEO.avi',
        type=str,
        help=('If specified, all motion events will be written to a single'
              ' file, creating a compilation of only the frames in'
              ' the input video containing motion. By default each'
              ' motion event is written to a separate file. Filename'
              ' MUST end with .avi.'))

    parser.add_argument(
        '-b',
        '--bg-subtractor',
        metavar='TYPE',
        dest='bg_subtractor',
        type=string_type_check(['MOG', 'CNT', 'MOG_CUDA'], False, 'TYPE'),
        default='MOG',
        help=('The type of background subtractor to use, must be one of: '
              ' MOG (default), CNT (parallel), MOG_CUDA (Nvidia GPU).'))

    parser.add_argument(
        '-so',
        '--scan-only',
        dest='scan_only_mode',
        action='store_true',
        default=False,
        help=('Only perform motion detection (does not write any files to disk).'))

    # TODO(v1.5): This needs to be changed to a new -c/--config flag.
    # Just leave default as XVID, since the other codecs don't seem to be as well supported,
    # and add a config file option to override it instead.
    parser.add_argument(
        '-c',
        '--codec',
        metavar='FOURCC',
        dest='fourcc_str',
        type=string_type_check(['XVID', 'MP4V', 'MP42', 'H264'], False, 'FOURCC'),
        default='XVID',
        help=('The four-letter identifier of the encoder/video codec to use'
              ' when exporting motion events as videos. Possible values'
              ' are: XVID, MP4V, MP42, H264.'))

    parser.add_argument(
        '-t',
        '--threshold',
        metavar='value',
        dest='threshold',
        type=float_type_check(0.0, None, 'value'),
        default=0.15,
        help=('Threshold value representing the amount of motion in a frame'
              ' required to trigger a motion event. Lower values require'
              ' less movement, and are more sensitive to motion. If the threshold'
              ' is too high, some movement in the scene may not be detected,'
              ' while too low of a threshold can trigger a false motion event.'))

    parser.add_argument(
        '-k',
        '--kernel-size',
        metavar='N',
        dest='kernel_size',
        type=odd_int_type_check(3, None, 'N', True),
        default=-1,
        help=('Size in pixels of the noise reduction kernel. Must be an odd'
              ' integer greater than 1, or set to -1 to auto-set based on'
              ' input video resolution (default). If the kernel size is set too'
              ' large, some movement in the scene may not be detected.'))

    parser.add_argument(
        '-l',
        '--min-event-length',
        metavar='T',
        dest='min_event_len',
        type=timecode_type_check('T'),
        default=2,
        help=('Number of frames that must exceed the threshold in a row to trigger'
              ' a new motion event, effectively setting a minimum event length.'
              ' Can also be specified as a timecode or # of seconds.'))

    parser.add_argument(
        '-tp',
        '--time-post-event',
        metavar='T',
        dest='time_post_event',
        type=timecode_type_check('T'),
        default='2s',
        help=('Number of frames to include after each motion event ends.'
              ' Any new motion events that occur in this period are'
              ' automatically joined with the current motion event.'
              ' Can also be specified as a timecode or # of seconds.'))

    parser.add_argument(
        '-tb',
        '--time-before-event',
        metavar='T',
        dest='time_pre_event',
        type=timecode_type_check('T'),
        default='1.5s',
        help=('Number of frames to include before a motion event is detected.'
              ' Can also be specified as a timecode or # of seconds.'))

    parser.add_argument(
        '-q',
        '--quiet',
        dest='quiet_mode',
        action='store_true',
        default=False,
        help=('Suppress all output except for final comma-separated list of motion events.'
              ' Useful for computing or piping output directly into other programs/scripts.'))

    parser.add_argument(
        '-st',
        '--start-time',
        metavar='time',
        dest='start_time',
        type=timecode_type_check('time'),
        default=None,
        help=('Time to seek to in video before performing detection. Can be'
              ' given in number of frames (12345), seconds (number followed'
              ' by s, e.g. 123s or 123.45s), or timecode (HH:MM:SS[.nnn]).'))

    parser.add_argument(
        '-dt',
        '--duration',
        metavar='time',
        dest='duration',
        type=timecode_type_check('time'),
        default=None,
        help=('Length of time in input video to limit motion detection to (see'
              ' -st for valid timecode formats). Overrides -et.'))

    parser.add_argument(
        '-et',
        '--end-time',
        metavar='time',
        dest='end_time',
        type=timecode_type_check('time'),
        default=None,
        help=('Timecode to stop motion detection at (see -st for valid'
              'timecode formats).'))

    parser.add_argument(
        '-df',
        '--downscale-factor',
        metavar='factor',
        dest='downscale_factor',
        type=int_type_check(1, None, 'factor'),
        default=1,
        help=('Factor to downscale (shrink) video before processing, to'
              ' improve performance. For example, if input video resolution'
              ' is 1024 x 400, and factor=2, each frame is reduced to'
              ' 1024/2 x 400/2=512 x 200 before processing.'))

    parser.add_argument(
        '-fs',
        '--frame-skip',
        metavar='num_frames',
        dest='frame_skip',
        type=int_type_check(0, None, 'num_frames'),
        default=0,
        help=('Number of frames to skip after processing a given frame.'
              ' Improves performance, at expense of frame and time accuracy,'
              ' and may increase probability of missing motion events.'
              ' If set, -l, -tb, and -tp will all be scaled relative to the source'
              ' framerate. Values above 1 or 2 are not recommended.'))

    parser.add_argument(
        '-tc',
        '--time-code',
        dest='draw_timecode',
        action='store_true',
        default=False,
        help=('Draw time code of each frame on the top left corner.'))

    parser.add_argument(
        '-roi',
        '--region-of-interest',
        dest='roi',
        metavar='x0 y0 w h',
        nargs='*',
        default=None,
        help=('If set, scan only in selected area, which is selected in a popup window'
              ' (select with mouse, then press enter).'
              ' Can also specify the window in terms of x/y/w/h.'
              ' Example for pop-up window: dvr-scan -i video.mp4 -roi '
              ' Example for predefined rectangle: dvr-scan -i video.mp4 -roi 100 110 50 50 '))

    parser.add_argument(
        '-bb',
        '--bounding-box',
        metavar='SMOOTH_TIME',
        dest='bounding_box',
        type=timecode_type_check('SMOOTH_TIME'),
        nargs='?',
        default=None,
        const='0.1s',
        help=('If set, draws a bounding box around the area where motion was detected. The amount'
              ' of temporal smoothing can be specified in either frames (12345) or seconds (number'
              ' followed by s, e.g. 123s or 123.45s). If omitted, defaults to 0.1s. If set to 0,'
              ' smoothing is disabled.'))

    # TODO(v1.5): Add a new -m/--output-mode flag to specify whether to use ffmpeg or the
    # OpenCV VideoWriter for output. Also will need to add some flags to specify the ffmpeg
    # arguments, and a new flag called --keep-temp-files for how concatenation has to work.

    # TODO(v1.5): Add a new -L/--license flag to dump the LICENSE and LICENSE-THIRDPARTY
    # files to stdout. Ensure works with binary, source, and frozen distributions.
    # Then cleanup the -v/--version flag to only show the version.

    return parser
