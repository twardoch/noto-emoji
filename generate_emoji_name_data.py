#!/usr/bin/env python3
#
# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generate name data for emoji resources. Currently in json format."""

import argparse
import json
import re
import sys
from os import path

import generate_emoji_html

from nototools import tool_utils, unicode_data


def _create_custom_gendered_seq_names():
    """The names have detail that is adequately represented by the image."""

    BOY = 0x1F466
    GIRL = 0x1F467
    MAN = 0x1F468
    WOMAN = 0x1F469
    HEART = 0x2764  # Heavy Black Heart
    KISS_MARK = 0x1F48B
    return {
        (MAN, HEART, KISS_MARK, MAN): "Kiss",
        (WOMAN, HEART, KISS_MARK, WOMAN): "Kiss",
        (WOMAN, HEART, KISS_MARK, MAN): "Kiss",
        (WOMAN, HEART, MAN): "Couple with Heart",
        (MAN, HEART, MAN): "Couple with Heart",
        (WOMAN, HEART, WOMAN): "Couple with Heart",
        (MAN, GIRL): "Family",
        (MAN, GIRL, GIRL): "Family",
        (MAN, GIRL, BOY): "Family",
        (MAN, BOY): "Family",
        (MAN, BOY, BOY): "Family",
        (MAN, WOMAN, GIRL): "Family",
        (MAN, WOMAN, GIRL, GIRL): "Family",
        (MAN, WOMAN, GIRL, BOY): "Family",
        (MAN, WOMAN, BOY): "Family",
        (MAN, WOMAN, BOY, BOY): "Family",
        (MAN, MAN, GIRL): "Family",
        (MAN, MAN, GIRL, GIRL): "Family",
        (MAN, MAN, GIRL, BOY): "Family",
        (MAN, MAN, BOY): "Family",
        (MAN, MAN, BOY, BOY): "Family",
        (WOMAN, GIRL): "Family",
        (WOMAN, GIRL, GIRL): "Family",
        (WOMAN, GIRL, BOY): "Family",
        (WOMAN, BOY): "Family",
        (WOMAN, BOY, BOY): "Family",
        (WOMAN, WOMAN, GIRL): "Family",
        (WOMAN, WOMAN, GIRL, GIRL): "Family",
        (WOMAN, WOMAN, GIRL, BOY): "Family",
        (WOMAN, WOMAN, BOY): "Family",
        (WOMAN, WOMAN, BOY, BOY): "Family",
    }


def _create_custom_seq_names():
    """These have names that often are of the form 'Person xyz-ing' or 'Man Xyz.'
    We opt to simplify the former to an activity name or action, and the latter to
    drop the gender.  This also generally makes the names shorter."""

    EYE = 0x1F441
    SPEECH = 0x1F5E8
    WHITE_FLAG = 0x1F3F3
    RAINBOW = 0x1F308
    return {
        (EYE, SPEECH): "I Witness",
        (WHITE_FLAG, RAINBOW): "Rainbow Flag",
        (0x2695,): "Health Worker",
        (0x2696,): "Judge",
        (0x26F7,): "Skiing",
        (0x26F9,): "Bouncing a Ball",
        (0x2708,): "Pilot",
        (0x1F33E,): "Farmer",
        (0x1F373,): "Cook",
        (0x1F393,): "Student",
        (0x1F3A4,): "Singer",
        (0x1F3A8,): "Artist",
        (0x1F3C2,): "Snowboarding",
        (0x1F3C3,): "Running",
        (0x1F3C4,): "Surfing",
        (0x1F3CA,): "Swimming",
        (0x1F3CB,): "Weight Lifting",
        (0x1F3CC,): "Golfing",
        (0x1F3EB,): "Teacher",
        (0x1F3ED,): "Factory Worker",
        (0x1F46E,): "Police Officer",
        (0x1F46F,): "Partying",
        (0x1F471,): "Person with Blond Hair",
        (0x1F473,): "Person Wearing Turban",
        (0x1F477,): "Construction Worker",
        (0x1F481,): "Tipping Hand",
        (0x1F482,): "Guard",
        (0x1F486,): "Face Massage",
        (0x1F487,): "Haircut",
        (0x1F4BB,): "Technologist",
        (0x1F4BC,): "Office Worker",
        (0x1F527,): "Mechanic",
        (0x1F52C,): "Scientist",
        (0x1F575,): "Detective",
        (0x1F645,): "No Good Gesture",
        (0x1F646,): "OK Gesture",
        (0x1F647,): "Bowing Deeply",
        (0x1F64B,): "Raising Hand",
        (0x1F64D,): "Frowning",
        (0x1F64E,): "Pouting",
        (0x1F680,): "Astronaut",
        (0x1F692,): "Firefighter",
        (0x1F6A3,): "Rowing",
        (0x1F6B4,): "Bicycling",
        (0x1F6B5,): "Mountain Biking",
        (0x1F6B6,): "Walking",
        (0x1F926,): "Face Palm",
        (0x1F937,): "Shrug",
        (0x1F938,): "Doing a Cartwheel",
        (0x1F939,): "Juggling",
        (0x1F93C,): "Wrestling",
        (0x1F93D,): "Water Polo",
        (0x1F93E,): "Playing Handball",
        (0x1F9D6,): "Person in Steamy Room",
        (0x1F9D7,): "Climbing",
        (0x1F9D8,): "Person in Lotus Position",
        (0x1F9D9,): "Mage",
        (0x1F9DA,): "Fairy",
        (0x1F9DB,): "Vampire",
        (0x1F9DD,): "Elf",
        (0x1F9DE,): "Genie",
        (0x1F9DF,): "Zombie",
    }


_CUSTOM_GENDERED_SEQ_NAMES = _create_custom_gendered_seq_names()
_CUSTOM_SEQ_NAMES = _create_custom_seq_names()

# Fixes for unusual capitalization or cases we don't care to handle in code.
# Also prevents titlecasing 'S' after apostrophe in posessives.  Note we _do_
# want titlecasing after apostrophe in some cases, e.g. O'Clock.
_CUSTOM_CAPS_NAMES = {
    (0x26D1,): "Rescue Worker’s Helmet",
    (0x1F170,): "A Button (blood type)",  # a Button (Blood Type)
    (0x1F171,): "B Button (blood type)",  # B Button (Blood Type)
    (0x1F17E,): "O Button (blood type)",  # O Button (Blood Type)
    (0x1F18E,): "AB Button (blood type)",  # Ab Button (Blood Type)
    (0x1F191,): "CL Button",  # Cl Button
    (0x1F192,): "COOL Button",  # Cool Button
    (0x1F193,): "FREE Button",  # Free Button
    (0x1F194,): "ID Button",  # Id Button
    (0x1F195,): "NEW Button",  # New Button
    (0x1F196,): "NG Button",  # Ng Button
    (0x1F197,): "OK Button",  # Ok Button
    (0x1F198,): "SOS Button",  # Sos Button
    (0x1F199,): "UP! Button",  # Up! Button
    (0x1F19A,): "VS Button",  # Vs Button
    (0x1F3E7,): "ATM Sign",  # Atm Sign
    (0x1F44C,): "OK Hand",  # Ok Hand
    (0x1F452,): "Woman’s Hat",
    (0x1F45A,): "Woman’s Clothes",
    (0x1F45E,): "Man’s Shoe",
    (0x1F461,): "Woman’s Sandal",
    (0x1F462,): "Woman’s Boot",
    (0x1F519,): "BACK Arrow",  # Back Arrow
    (0x1F51A,): "END Arrow",  # End Arrow
    (0x1F51B,): "ON! Arrow",  # On! Arrow
    (0x1F51C,): "SOON Arrow",  # Soon Arrow
    (0x1F51D,): "TOP Arrow",  # Top Arrow
    (0x1F6B9,): "Men’s Room",
    (0x1F6BA,): "Women’s Room",
}

# For the custom sequences we ignore ZWJ, the emoji variation selector
# and skin tone modifiers.  We can't always ignore gender  because
# the gendered sequences match against them, but we ignore gender in other
# cases so we define a separate set of gendered emoji to remove.

_NON_GENDER_CPS_TO_STRIP = frozenset(
    [0xFE0F, 0x200D] + range(unicode_data._FITZ_START, unicode_data._FITZ_END + 1)
)

_GENDER_CPS_TO_STRIP = frozenset([0x2640, 0x2642, 0x1F468, 0x1F469])


def _custom_name(seq):
    """Apply three kinds of custom names, based on the sequence."""

    seq = tuple([cp for cp in seq if cp not in _NON_GENDER_CPS_TO_STRIP])
    name = _CUSTOM_CAPS_NAMES.get(seq)
    if name:
        return name

    # Single characters that participate in sequences (e.g. fire truck in the
    # firefighter sequences) should not get converted.  Single characters
    # are in the custom caps names set but not the other sets.
    if len(seq) == 1:
        return None

    name = _CUSTOM_GENDERED_SEQ_NAMES.get(seq)
    if name:
        return name

    seq = tuple([cp for cp in seq if cp not in _GENDER_CPS_TO_STRIP])
    name = _CUSTOM_SEQ_NAMES.get(seq)

    return name


def _standard_name(seq):
    """Use the standard emoji name, with some algorithmic modifications.

    We want to ignore skin-tone modifiers (but of course if the sequence _is_
    the skin-tone modifier itself we keep that).  So we strip these so we can
    start with the generic name ignoring skin tone.

    Non-emoji that are turned into emoji using the emoji VS have '(emoji) '
    prepended to them, so strip that.

    Regional indicator symbol names are a bit long, so shorten them.

    Regional sequences are assumed to be ok as-is in terms of capitalization and
    punctuation, so no modifications are applied to them.

    After title-casing we make some English articles/prepositions lower-case
    again.  We also replace '&' with 'and'; Unicode seems rather fond of
    ampersand."""

    if not unicode_data.is_skintone_modifier(seq[0]):
        seq = tuple([cp for cp in seq if not unicode_data.is_skintone_modifier(cp)])
    name = unicode_data.get_emoji_sequence_name(seq)

    if name.startswith("(emoji) "):
        name = name[8:]

    if len(seq) == 1 and unicode_data.is_regional_indicator(seq[0]):
        return "Regional Symbol " + unicode_data.regional_indicator_to_ascii(seq[0])

    if unicode_data.is_regional_indicator_seq(seq) or unicode_data.is_regional_tag_seq(
        seq
    ):
        return name

    name = name.title()
    # Require space delimiting just in case...
    name = re.sub(r"\s&\s", " and ", name)
    name = re.sub(
        # not \b at start because we retain capital at start of phrase
        r"(\s(:?A|And|From|In|Of|With|For))\b",
        lambda s: s.group(1).lower(),
        name,
    )

    return name


def _name_data(seq, seq_file):
    name = _custom_name(seq) or _standard_name(seq)
    # we don't need canonical sequences
    sequence = "".join("&#x%x;" % cp for cp in seq if cp != 0xFE0F)
    fname = path.basename(seq_file)
    return fname, sequence, name


def generate_names(
    src_dir, dst_dir, skip_limit=20, omit_groups=None, pretty_print=False, verbose=False
):
    srcdir = tool_utils.resolve_path(src_dir)
    if not path.isdir(srcdir):
        print("%s is not a directory" % src_dir, file=sys.stderr)
        return

    if omit_groups:
        unknown_groups = set(omit_groups) - set(unicode_data.get_emoji_groups())
        if unknown_groups:
            print(
                "did not recognize %d group%s: %s"
                % (
                    len(unknown_groups),
                    "" if len(unknown_groups) == 1 else "s",
                    ", ".join('"%s"' % g for g in omit_groups if g in unknown_groups),
                ),
                file=sys.stderr,
            )
            print(
                "valid groups are:\n  %s"
                % ("\n  ".join(g for g in unicode_data.get_emoji_groups())),
                file=sys.stderr,
            )
            return
        print(
            "omitting %d group%s: %s"
            % (
                len(omit_groups),
                "" if len(omit_groups) == 1 else "s",
                ", ".join('"%s"' % g for g in omit_groups),
            )
        )
    else:
        # might be None
        print("keeping all groups")
        omit_groups = []

    # make sure the destination exists
    dstdir = tool_utils.ensure_dir_exists(tool_utils.resolve_path(dst_dir))

    # _get_image_data returns canonical cp sequences
    print("src dir:", srcdir)
    seq_to_file = generate_emoji_html._get_image_data(srcdir, "png", "emoji_u")
    print("seq to file has %d sequences" % len(seq_to_file))

    # Aliases add non-gendered versions using gendered images for the most part.
    # But when we display the images, we don't distinguish genders in the
    # naming, we rely on the images-- so these look redundant. So we
    # intentionally don't generate images for these.
    # However, the alias file also includes the flag aliases, which we do want,
    # and it also fails to exclude the unknown flag pua (since it doesn't
    # map to anything), so we need to adjust for this.
    canonical_aliases = generate_emoji_html._get_canonical_aliases()

    aliases = {
        cps
        for cps in canonical_aliases.keys()
        if not unicode_data.is_regional_indicator_seq(cps)
    }
    aliases.add((0xFE82B,))  # unknown flag PUA
    excluded = aliases | generate_emoji_html._get_canonical_excluded()

    # The flag aliases have distinct names, so we _do_ want to show them
    # multiple times.
    to_add = {}
    for seq in canonical_aliases:
        if unicode_data.is_regional_indicator_seq(seq):
            replace_seq = canonical_aliases[seq]
            if seq in seq_to_file:
                print(
                    "warning, alias {} has file {}".format(
                        unicode_data.regional_indicator_seq_to_string(seq),
                        seq_to_file[seq],
                    )
                )
                continue
            replace_file = seq_to_file.get(replace_seq)
            if replace_file:
                to_add[seq] = replace_file
    seq_to_file.update(to_add)

    data = []
    last_skipped_group = None
    skipcount = 0
    for group in unicode_data.get_emoji_groups():
        if group in omit_groups:
            continue
        name_data = []
        for seq in unicode_data.get_emoji_in_group(group):
            if seq in excluded:
                continue
            seq_file = seq_to_file.get(seq, None)
            if seq_file is None:
                skipcount += 1
                if verbose:
                    if group != last_skipped_group:
                        print("group %s" % group)
                        last_skipped_group = group
                    print(
                        "  {} ({})".format(
                            unicode_data.seq_to_string(seq),
                            ", ".join(unicode_data.name(cp, "x") for cp in seq),
                        )
                    )
                if skip_limit >= 0 and skipcount > skip_limit:
                    raise Exception("skipped too many items")
            else:
                name_data.append(_name_data(seq, seq_file))
        data.append({"category": group, "emojis": name_data})

    outfile = path.join(dstdir, "data.json")
    with open(outfile, "w") as f:
        indent = 2 if pretty_print else None
        separators = None if pretty_print else (",", ":")
        json.dump(data, f, indent=indent, separators=separators)
    print("wrote %s" % outfile)


def main():
    DEFAULT_DSTDIR = "[emoji]/emoji"
    DEFAULT_IMAGEDIR = "[emoji]/build/compressed_pngs"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--srcdir",
        help="directory containing images (default %s)" % DEFAULT_IMAGEDIR,
        metavar="dir",
        default=DEFAULT_IMAGEDIR,
    )
    parser.add_argument(
        "-d",
        "--dstdir",
        help="name of destination directory (default %s)" % DEFAULT_DSTDIR,
        metavar="fname",
        default=DEFAULT_DSTDIR,
    )
    parser.add_argument(
        "-p", "--pretty_print", help="pretty-print json file", action="store_true"
    )
    parser.add_argument(
        "-m",
        "--missing_limit",
        help="number of missing images before failure "
        "(default 20), use -1 for no limit",
        metavar="n",
        default=20,
    )
    parser.add_argument(
        "--omit_groups",
        help='names of groups to omit (default "Misc, Flags")',
        metavar="name",
        default=["Misc", "Flags"],
        nargs="*",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="print progress information to stdout",
        action="store_true",
    )
    args = parser.parse_args()
    generate_names(
        args.srcdir,
        args.dstdir,
        args.missing_limit,
        args.omit_groups,
        pretty_print=args.pretty_print,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
