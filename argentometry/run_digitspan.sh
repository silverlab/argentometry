#!/usr/local/bin/zsh

#http://wiki.wxpython.org/wxPythonVirtualenvOnMac

WXPYTHON_APP="digitspan.py"
PYVER=2.7

if [ -z "$VIRTUAL_ENV" ] ; then
	echo "Please activate the virtualenv"
	exit 1
fi

FRAMEWORK_PYTHON="$(brew --prefix)/Cellar/python/2.7.11/Frameworks/Python.framework/Versions/Current/bin/python2.7"

VENV_SITE_PACKAGES="$VIRTUAL_ENV/lib/python2.7/site-packages"

export PYTHONHOME=$VIRTUAL_ENV
echo $FRAMEWORK_PYTHON
exec "$FRAMEWORK_PYTHON" "$WXPYTHON_APP" $*