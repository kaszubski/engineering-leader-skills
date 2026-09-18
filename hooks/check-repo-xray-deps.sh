#!/bin/sh
# repo-xray requires python3 and git; the other skills need neither.
# Silent when both are present — only speaks up when repo-xray would fail.

missing_python3=0
missing_git=0
command -v python3 >/dev/null 2>&1 || missing_python3=1
command -v git >/dev/null 2>&1 || missing_git=1

if [ "$missing_python3" = 0 ] && [ "$missing_git" = 0 ]; then
  exit 0
fi

if [ "$missing_python3" = 1 ] && [ "$missing_git" = 1 ]; then
  msg="repo-xray needs python3 and git on PATH; neither was found, so that skill won't run until they're installed. The other skills (pr-review, coaching-calibrator, retro-facilitator) are unaffected."
elif [ "$missing_python3" = 1 ]; then
  msg="repo-xray needs python3 on PATH; it wasn't found, so that skill won't run until it's installed. The other skills (pr-review, coaching-calibrator, retro-facilitator) are unaffected."
else
  msg="repo-xray needs git on PATH; it wasn't found, so that skill won't run until it's installed. The other skills (pr-review, coaching-calibrator, retro-facilitator) are unaffected."
fi

printf '{"systemMessage": "%s"}\n' "$msg"
