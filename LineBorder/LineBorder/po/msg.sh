
APP=LineBorder

mode=$1

if [ "$mode" = "-u" ]
then
  # extract strings from the glade file
  echo 
  echo "Prepare .glade files"
  intltool-extract --type="gettext/glade" ../${APP}.glade

  # create pot file
  echo
  echo "Update .pot file"
  intltool-update --pot --gettext-package=$APP

  echo
  echo "Update language files"
  cat LINGUAS |egrep -v "^ *#|^$" | while read _lang _locale
  do
    echo "-> $_lang <-"
    if [ -f "${_lang}.po" ]
    then
     intltool-update --dist --gettext-package=LineBorder ${_lang} 
    else
      msginit --input=${APP}.pot --no-translator --locale=$_lang
    fi
    echo
  done
elif [ "$mode" = "-c" ]
then
  echo
  echo "Compile language files"
  cat LINGUAS |egrep -v "^ *#|^$" | while read _lang _locale
  do
    echo "-> $_lang <-"
    mkdir -p ../locale/${_locale}/LC_MESSAGES
    msgfmt --output-file=../locale/${_locale}/LC_MESSAGES/$APP.mo ${_lang}.po
  done
else
  echo "Usage: $0 <mode>"
  echo "  mode:"
  echo "        -u - update messages"
  echo "        -c - compile po files (create mo files)"
fi

