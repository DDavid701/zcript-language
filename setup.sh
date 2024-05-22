#!/usr/bin/bash
echo "What are you doing xd?"
echo "Didn't i say this is not useful??"
echo "Do you really want to set this up??????? .-."
while true; do
    read -p ">" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
    esac
done
echo "Setting up Zcript .-."
sudo cp zcript.py /usr/bin/
sudo cp zcript.py /bin/
echo "Hey Everything is setup!"
echo "to test if its working do 'zcript --v'"
echo "if that worked i recommend you doing 'zcript --help'"
echo ""
echo "if that all worked properly u can run the test file using 'zcript test.zc'"
echo "Hope everything works. If that is the case then enjoy! :D"