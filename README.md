# EloiTwit @ https://github.com/fedef17/EloiTwit

Hi! This is eloi_twit. At the time, you can do 2 things with it:
- STREAMING and DOWNLOAD of twitter flows
- SEARCHING and DOWNLOAD of twitter flows in the past, till about 10-15 days ago. Depends on Twitter.

###### BEFORE EVERYTHING ###########

Just for UNIX users, zorry!
You need to have python installed. If not: sudo apt-get install python

0) Then, clone the repository to some place and go into that folder.
1) Run install_modules.sh:

[COMMAND]
./install_modules.sh

If you find some error (quite possible), you just need to install the missing packages giving either:

sudo apt-get install PACKAGE

or:

sudo pip install PACKAGE

If no errors are found you're ready!

#######################################
##### BEFORE RUNNING ##################
#######################################

You need dev access to Twitter. For that, you should:

2) replace the pass strings in access_file.acc with your own.

2bis) If you don't have dev access you need one. Go at apps.twitter.com and sign in with your account. Enter "Creat your app" and follow the steps. Then you have to click on "Generate my access tokens" inside the app preferences. This will generate your 4 keys. (can find many tutorials on the internet on how to do this, anyway). Go to 2).


#######################################
######### SETTING YOUR RUN ############
#######################################

3) Both for eloi_search.py and for eloi_stream.py you just need to place your own values in SAMPLE_eloi_input.in, which is well explained inside. Choose your #ht and write your PCs paths.

3b) copy to the input file:

[COMMAND]
cp SAMPLE_eloi_input.in eloi_input.in

#######################################
########### RUN #######################

You're ready to run! You have two options:

4a) STREAMING:

If you want to see the log output real_time, run from the code folder:

[COMMAND]
python eloi_stream.py eloi_input.in -ll True -v True

If you are sure it works and just want to save the log and leave the process in background, omit the options:

[COMMAND]
python eloi_stream.py eloi_input.in


4b) SEARCH:

Much the same, just changes the program name.

If you want to see the log output real_time, run from the code folder:

[COMMAND]
python eloi_search.py eloi_input.in -ll True -v True

If you are sure it works and just want to save the log and leave the process in background, omit the options:

[COMMAND]
python eloi_search.py eloi_input.in


##############################################
############# AFTER THE RUN.. ################

For now you have some lot of .dat files (text files) with all the DOWNLOADED tweets inside. json format.

Still work in progress! Hope to have some tools for flow analysis soon..
