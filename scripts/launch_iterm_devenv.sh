#!/bin/bash

basedir=$(realpath $(dirname $0)/..)

api_key=$(cat $basedir/API_KEY)

osascript <<-EOF

tell application "iTerm2"

  tell current session of current window
    split vertically with default profile
    split vertically with default profile
  end tell

  tell first session of current tab of current window
    write text "cd $basedir; meilisearch --master-key $api_key &"
  end tell

  tell second session of current tab of current window
    write text "cd $basedir; . .venv/bin/activate; python zotero-indexer/run_server.py"
  end tell

  tell third session of current tab of current window
    write text "cd $basedir/zotero-indexer-frontend; npm run dev"
  end tell

end tell

EOF

