#!/bin/sh
#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#
sysc_path() {
    CMDPATH="$(cd "$(dirname "$0")" && pwd -P)"/"$(basename "$0")"
    SYSC_ROOT=$(dirname "$CMDPATH" | sed -e 's/\/Participants\/.*$//g')
    export SYSC_ROOT
}

test -z "$SYSC_ROOT" && sysc_path

if [ -z "$SYSC_DEPENDENCIES" ]; then
    if [ -d "$SYSC_ROOT/../Core_Dependencies" ]; then
      SYSC_DEPENDENCIES="$SYSC_ROOT/../Core_Dependencies"
      export SYSC_DEPENDENCIES
    fi
fi

PY3VER=3_10
if [ -z "$SYSC_PY_VERSION" ]; then
    SYSC_PY_VERSION=$PY3VER
    export SYSC_PY_VERSION
fi

if [ -d "${SYSC_DEPENDENCIES}/CPython/$SYSC_PY_VERSION/linx64/Release/python/bin" ]; then
    export SYSC_PYTHON="${SYSC_DEPENDENCIES}/CPython/$SYSC_PY_VERSION/linx64/Release/python/bin"
elif [ -d "$SYSC_ROOT/CPython/$SYSC_PY_VERSION/linx64/Release/python/bin" ]; then
    export SYSC_PYTHON="$SYSC_ROOT/CPython/$SYSC_PY_VERSION/linx64/Release/python/bin"
elif [ -d "$SYSC_ROOT/../commonfiles/CPython/$SYSC_PY_VERSION/linx64/Release/python/bin" ]; then
    export SYSC_PYTHON="$SYSC_ROOT/../commonfiles/CPython/$SYSC_PY_VERSION/linx64/Release/python/bin"
else
    echo "Could not find CPython ..."
    exit 1
fi

if [ -z "$SYSC_VERSION" ]; then
    export SYSC_VERSION="2024 R1"
fi

if [ -z "$SYSC_PARTLIB_BUILDNAME" ]; then
    export BINDIRNAME=bin
else
    export BINDIRNAME=bin_"${SYSC_PARTLIB_BUILDNAME}"
fi

export LD_LIBRARY_PATH="${SYSC_ROOT}"/runTime/linx64/"${BINDIRNAME}"/compiler:"${LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="${SYSC_ROOT}"/runTime/linx64/"${BINDIRNAME}":"${LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="${SYSC_ROOT}"/runTime/linx64/cnlauncher/fluent/fluent24.2.0/multiport/mpi_wrapper/lnamd64/stub:"${LD_LIBRARY_PATH}"

export PYTHONPATH="${SYSC_ROOT}"/runTime/linx64/"${BINDIRNAME}":"${PYTHONPATH}"

"${SYSC_PYTHON}/python" -B "Compressor.py" "$@"
exit $?
