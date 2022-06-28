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
from dvr_scan.cli.config import ConfigRegistry, CHOICE_MAP, USER_CONFIG_FILE_PATH

# Version string shown for the -v/--version CLI argument.
VERSION_STRING = """------------------------------------------------
DVR-Scan %s
------------------------------------------------
Copyright (C) 2016-2022 Brandon Castellano
< https://github.com/Breakthrough/DVR-Scan >
""" % dvr_scan.__version__


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
class LicenseAction(argparse.Action):
    """argparse Action for displaying DVR-Scan license & copyright info."""

    # pylint: disable=redefined-builtin, too-many-arguments
    def __init__(self,
                 option_strings,
                 version=None,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help="show version number and license/copyright information"):
        super(LicenseAction, self).__init__(
            option_strings=option_strings, dest=dest, default=default, nargs=0, help=help)
        self.version = version

    def __call__(self, parser, namespace, values, option_string=None):
        version = self.version
        if version is None:
            version = parser.version
        parser.exit(message=version)


# pylint: disable=too-few-public-methods
class AboutAction(argparse.Action):
    """argparse Action for displaying DVR-Scan version."""

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


def get_cli_parser(user_config: ConfigRegistry):
    """Creates the DVR-Scan argparse command-line interface.

    Arguments:
        user_config: User configuration file registry.

    Returns:
        ArgumentParser object, which parse_args() can be called with.
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS,
    )

    if hasattr(parser, '_optionals'):
        # pylint: disable=protected-access
        parser._optionals.title = 'arguments'

    parser.add_argument(
        '-v',
        '--version',
        action=AboutAction,
        version=VERSION_STRING,
    )

    parser.add_argument(
        '-L',
        '--license',
        action=AboutAction,
        version=dvr_scan.get_license_info(),
    )

    parser.add_argument(
        '-q',
        '--quiet',
        dest='quiet_mode',
        action='store_true',
        help=('Suppress all output except for final comma-separated list of motion events.'
              ' Useful for computing or piping output directly into other programs/scripts.%s' %
              user_config.get_help_string('program', 'quiet-mode')),
    )

    parser.add_argument(
        '--verbosity',
        metavar='type',
        type=string_type_check(CHOICE_MAP['program']['verbosity'], False, 'TYPE'),
        help=('Amount of verbosity to use for log output. Must be one of: %s.%s' %
              (', '.join(CHOICE_MAP['program']['verbosity']),
               user_config.get_help_string('program', 'verbosity'))),
    )

    parser.add_argument(
        '--logfile',
        metavar='file',
        type=str,
        help=('Path to log file for writing application output. If FILE already exists, the program'
              ' output will be appended to the existing contents.'),
    )

    parser.add_argument(
        '-i',
        '--input',
        metavar='video_file',
        required=True,
        type=str,
        action='append',
        help=('[REQUIRED] Path to input video. May be specified multiple'
              ' times to join several videos with the same resolution'
              ' and framerate. Any output filenames will be generated'
              ' using the first filename only.'),
    )

    parser.add_argument(
        '-o',
        '--output',
        metavar='video.avi',
        type=str,
        help=('If specified, all motion events will be written to a single'
              ' file, creating a compilation of only the frames in'
              ' the input video containing motion. By default each'
              ' motion event is written to a separate file. Filename'
              ' MUST end with .avi.'),
    )

    parser.add_argument(
        '-c',
        '--config',
        metavar='settings.cfg',
        type=str,
        help=('Path to config file. If not set, tries to load one from %s' %
              (USER_CONFIG_FILE_PATH)),
    )

    parser.add_argument(
        '-b',
        '--bg-subtractor',
        metavar='type',
        type=string_type_check(['MOG', 'CNT', 'MOG_CUDA'], False, 'type'),
        help=('The type of background subtractor to use, must be one of: '
              ' MOG (default), CNT (parallel), MOG_CUDA (Nvidia GPU).%s') %
        user_config.get_help_string('detection', 'bg-subtractor'),
    )

    parser.add_argument(
        '-so',
        '--scan-only',
        action='store_true',
        default=False,
        help=('Only perform motion detection (does not write any files to disk).'),
    )

    parser.add_argument(
        '--codec',
        metavar='fourcc',
        dest='opencv_codec',
        type=string_type_check(CHOICE_MAP['program']['opencv-codec'], False, 'fourcc'),
        help=('The four-letter identifier of the encoder/video codec to use'
              ' when exporting motion events using OpenCV. Must be one of: %s.%s' %
              (', '.join(CHOICE_MAP['program']['opencv-codec']).upper(),
               user_config.get_help_string('program', 'opencv-codec'))),
    )

    parser.add_argument(
        '-t',
        '--threshold',
        metavar='value',
        type=float_type_check(0.0, None, 'value'),
        help=('Threshold value representing the amount of motion in a frame'
              ' required to trigger a motion event. Lower values require'
              ' less movement, and are more sensitive to motion. If the threshold'
              ' is too high, some movement in the scene may not be detected,'
              ' while too low of a threshold can trigger a false motion event.%s' %
              (user_config.get_help_string('detection', 'threshold'))),
    )

    parser.add_argument(
        '-k',
        '--kernel-size',
        metavar='N',
        type=odd_int_type_check(3, None, 'N', True),
        help=('Size in pixels of the noise reduction kernel. Must be an odd'
              ' integer greater than 1, or set to -1 to auto-set based on'
              ' input video resolution (default). If the kernel size is set too'
              ' large, some movement in the scene may not be detected.%s' %
              (user_config.get_help_string('detection', 'kernel-size'))),
    )

    parser.add_argument(
        '-l',
        '--min-event-length',
        metavar='T',
        type=timecode_type_check('T'),
        help=('Length of time that must contain motion before triggering a new event. Can be'
              ' specified as frames (123), seconds (12.3s), or timecode (00:00:01).%s' %
              user_config.get_help_string('detection', 'min-event-length')),
    )

    parser.add_argument(
        '-tp',
        '--time-post-event',
        metavar='T',
        type=timecode_type_check('T'),
        help=('Maximum amount of time to include after each event. The event will end once no'
              ' motion has been detected for this period of time. Can be specified as frames (123),'
              ' seconds (12.3s), or timecode (00:00:01).%s' %
              user_config.get_help_string('detection', 'time-post-event')),
    )

    parser.add_argument(
        '-tb',
        '--time-before-event',
        metavar='T',
        type=timecode_type_check('T'),
        help=('Maximum amount of time to include before each event. Can be specified as'
              ' frames (123), seconds (12.3s), or timecode (00:00:01).%s' %
              user_config.get_help_string('detection', 'time-before-event')),
    )

    parser.add_argument(
        '-st',
        '--start-time',
        metavar='time',
        type=timecode_type_check('time'),
        default=None,
        help=('Time to seek to in video before performing detection. Can be'
              ' given in number of frames (12345), seconds (number followed'
              ' by s, e.g. 123s or 123.45s), or timecode (HH:MM:SS[.nnn]).'),
    )

    parser.add_argument(
        '-dt',
        '--duration',
        metavar='time',
        type=timecode_type_check('time'),
        default=None,
        help=('Length of time in input video to limit motion detection to (see'
              ' -st for valid timecode formats). Overrides -et.'),
    )

    parser.add_argument(
        '-et',
        '--end-time',
        metavar='time',
        type=timecode_type_check('time'),
        default=None,
        help=('Timecode to stop motion detection at (see -st for valid'
              'timecode formats).'),
    )

    parser.add_argument(
        '-df',
        '--downscale-factor',
        metavar='factor',
        type=int_type_check(0, None, 'factor'),
        help=('Integer factor to downscale (shrink) video before processing, to'
              ' improve performance. For example, if input video resolution'
              ' is 1024 x 400, and factor=2, each frame is reduced to'
              ' 1024/2 x 400/2=512 x 200 before processing.%s' %
              (user_config.get_help_string('detection', 'downscale-factor'))),
    )

    parser.add_argument(
        '-fs',
        '--frame-skip',
        metavar='num_frames',
        type=int_type_check(0, None, 'num_frames'),
        help=('Number of frames to skip after processing a given frame.'
              ' Improves performance, at expense of frame and time accuracy,'
              ' and may increase probability of missing motion events.'
              ' If set, -l, -tb, and -tp will all be scaled relative to the source'
              ' framerate. Values above 1 or 2 are not recommended.%s' %
              (user_config.get_help_string('detection', 'frame-skip'))),
    )

    parser.add_argument(
        '-tc',
        '--time-code',
        dest='draw_timecode',
        action='store_true',
        help=('Draw time code of each frame on the top left corner.%s' %
              user_config.get_help_string('overlays', 'timecode', show_default=False)),
    )

    parser.add_argument(
        '-roi',
        '--region-of-interest',
        metavar='x0 y0 w h',
        nargs='*',
        help=('Limit detection to specified region. Can specify as -roi to show popup window,'
              ' or specify the region in the form -roi x,y w,h (e.g. -roi 100 200 50 50)%s' %
              (user_config.get_help_string('detection', 'region-of-interest', show_default=False))),
    )

    parser.add_argument(
        '-bb',
        '--bounding-box',
        metavar='smooth_time',
        type=timecode_type_check('smooth_time'),
        nargs='?',
        const=False,
        help=('If set, draws a bounding box around the area where motion was detected. The amount'
              ' of temporal smoothing can be specified in either frames (12345) or seconds (number'
              ' followed by s, e.g. 123s or 123.45s). If omitted, defaults to 0.1s. If set to 0,'
              ' smoothing is disabled.%s' %
              (user_config.get_help_string('overlays', 'bounding-box', show_default=False))),
    )

    parser.add_argument(
        '-mo',
        '--mask-output',
        metavar='video.avi',
        type=str,
        help=('If specified, writes a video containing the motion mask for fine tuning or other'
              ' analysis. A configuration file can be used to customize the mask output.'),
    )

    # TODO(v1.6): Add a new -m/--output-mode flag to specify whether to use ffmpeg or the
    # OpenCV VideoWriter for output. Also will need to add some flags to specify the ffmpeg
    # arguments, and a new flag called --keep-temp-files for how concatenation has to work.

    # TODO(v1.6): Add a mode that can dump frame scores (-s/--stats), and another mode
    # that can dump the resulting frames after processing (-d/--dump-motion OUT.avi).
    # Might also be helpful to overlay the frame score when using -d. Multiply the motion
    # mask against the input image.
    return parser
