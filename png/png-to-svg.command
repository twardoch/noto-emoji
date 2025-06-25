#!/usr/bin/env bash
dir=${0%/*}; if [ "$dir" = "$0" ]; then dir="."; fi; cd "$dir";

# Library functions

function insbrew {
    # Install Homebrew if not installed
    [ ! -x "$(which brew)" ] && /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" || return
}

function pkgbrew {
    # Install package if not installed
    # $ pkgbrew go
    [ -z "$1" ] && return || local pkg="$1";
    insbrew;
    if [ -x "$(touch $(brew --prefix)/var/testX6mg87lk)" ]; then
        echo "Homebrew needs to fix permissions, enter your administrator password:"
        sudo chown -R $(whoami) $(brew --prefix)/*;
        sudo chown $(whoami) $(brew --prefix)/*;
        brew list -1 | while read pkg; do brew unlink "$pkg"; brew link "$pkg"; done
    else
        rm "$(brew --prefix)/var/testX6mg87lk";
    fi;
    if brew ls --versions "$pkg" >/dev/null; then
        HOMEBREW_NO_AUTO_UPDATE=1 brew upgrade "$pkg";
    else
        HOMEBREW_NO_AUTO_UPDATE=1 brew install "$pkg"
    fi
}

function needbrew {
    # $ needbrew package # if command=package
    # $ needbrew command package # if command!=package
    [ -z "$1" ] && return || local cmd="$1";
    [ -z "$2" ] && local pkg="$cmd" || local pkg="$2";
    [ ! -x "$(which $cmd)" ] && pkgbrew "$pkg" || return;
}

function needbrewpy2 {
    if [ ! -x "$(which python2)" ]; then
        needbrew python2 python@2;
        brew link --overwrite python@2;
    fi;
}

function needbrewpy3 {
    if [ ! -x "$(which python3)" ]; then
        needbrew python3 python;
        brew link --overwrite python;
    fi;
}

function needgo {
    # $ needgo command github.com/author/repo [args...]
    [ -z "$1" ] && return || local cmd="$1";
    [ -z "$2" ] && return || local pkg="$2";
    needbrew go;
    [ ! -x "$(which $cmd)" ] && go get -u "$pkg" "${@:3}" || return;
}

function needrust {
    # $ needrust command --git https://github.com/author/repo [args...]
    [ -z "$1" ] && return || local cmd="$1";
    [ -z "$2" ] && return || local pkg="$2";
    needbrew cargo rust;
    [ ! -x "$(which $cmd)" ] && cargo install "$pkg" "${@:3}" || return;
}

function needpy2 {
    # $ needpy2 command package [package...]
    [ -z "$1" ] && return || local cmd="$1";
    [ -z "$2" ] && return || local pkg="$2";
    needbrewpy2;
    [ ! -x "$(which $cmd)" ] && python2 -m pip install --user --upgrade "$pkg" "${@:3}" || return
}

function needpy3 {
    # $ needpy3 command package [package...]
    [ -z "$1" ] && return || local cmd="$1";
    [ -z "$2" ] && return || local pkg="$2";
    needbrewpy3;
    [ ! -x "$(which $cmd)" ] && python3 -m pip install --user --upgrade "$pkg" "${@:3}" || return
}

function neednode {
    # $ neednode package # if command=package
    # $ neednode command package [package...] # if command!=package
    [ -z "$1" ] && return || local cmd="$1";
    [ -z "$2" ] && local pkg="$cmd" || local pkg="$2";
    needbrew npm node;
    [ ! -x "$(which $cmd)" ] && npm i -g npm "$pkg" "${@:3}" || return
}

# Specific functions

function install {
    needbrew convert ImageMagick
    neednode svgo;
    needrust svg-halftone --git https://github.com/evestera/svg-halftone;
    needgo points github.com/borud/points;
    needgo png2svg github.com/xyproto/png2svg/cmd/png2svg;
}

install;

#convert emoji_u1f4aa_1f3fe.png -background white -alpha remove -contrast-stretch 0 emoji_u1f4aa_1f3fe.white.png && points -f emoji_u1f4aa_1f3fe.white.png -o emoji_u1f4aa_1f3fe.points.svg -b 8 -t 0.8 -l

