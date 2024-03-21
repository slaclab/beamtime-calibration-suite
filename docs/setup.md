Beamtime calibration suite git/github setup

1) Make a github.com account


-if already have github account and want to use it, skip to 2)

-else, follow the steps here: https://github.com/join


-username can be anything, some people use ‘<slac_username>-slac’ convention (ex: nstelter-slac)


- for email can use ‘@slac.stanford.edu’ address, or any other address if you want (just make sure to use the same email in step 3))


-will need a code from email to verify during creating account




2) Register github account with ‘SLAC Lab’ github group

-join ‘#comp-general’ channel on Slack

-when viewing this Slack channel, should see ‘Pinned’ and next to it ‘Workflows’ at top of the page
-click ‘Workflows’ -> ‘SLAC GitHub Access’, and fill out the form with your info

-should receive an email later asking you to join the ‘SLAC Lab’ group, then follow the further instructions in this email







For steps 3), 4), 5), make sure you terminal (linux or mac) is setup first with the following commands:

-(note: in the 1st command: replace <slac-username> with your slac linux-username)

    ssh -Yt <slac-username>@s3dflogin.slac.stanford.edu

    source /sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh

3) Config local git settings

-Enter the following terminal commands:

    git config --global user.name <github username>

    git config --global user.email <email used to setup github account>

    git config --global core.editor vim

-Can use editor of your choice (ex: emacs) instead of “vim”, this will be editor used to edit commit messages and some other git options




4) Setup SSH Keys for github on s3df

-Make sure you are logged into github account in browser

-Follow instructions under “Generating a new SSH key” and “Adding your SSH key to the ssh-agent” : https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key (make sure you have selected the 'Linux' tab near the top of the page, not 'Mac')

-Follow instructions under “Adding a new SSH key to your account”: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account#adding-a-new-ssh-key-to-your-account (make sure you have selected the 'Linux' tab near the top of the page, not 'Mac')




5) Download repo

-cd to where you want the scripts to live (the scripts will be downloaded inside of a folder called ‘beamtime-calibration-suite’)

    -I suggest inside your home directory (‘~’), or inside a new folder you make like ‘~/repos/’

-to download the scripts, run the following command: git clone git@github.com:slaclab/beamtime-calibration-suite.git

     -if an error occurs, SSH setup in step 3) may have an issue and needs to be debugged

-if clone is successful, you should be able to cd into newly created ‘beamtime-calibration-suite’ folder and see subfolders containing python code


-now get the 'development' branch by running command: git checkout development

(For reference:

   -the main scripts repo lives here: https://github.com/slaclab/beamtime-calibration-suite


   -and to see most up-to-date code in development look at the 'development' branch: https://github.com/slaclab/beamtime-calibration-suite/tree/development)




6) Learn Git

-Suggest reading first 3 chapters of https://git-scm.com/book/en/v2 :

     -The following sections can be skipped if you want (more detail than needed atm),


         -1.5, 1.6, 2.6, 2.7, 3.5, 3.6

     -recommended resource by git community, gives good base-understanding of git

     -but many similar tutorials exist, so feel free to use other 'intro to git/github' videos/websites if you like them better

-(Optional) Here is also short presentation that summaries book content: https://courses.cs.washington.edu/courses/cse403/13au/lectures/git.ppt.pdf


-(Optional) Git commands cheat sheet: https://www.jrebel.com/system/files/git-cheat-sheet.pdf (**link will start download of pdf cheat sheet)

-(If you plan on developing the library) The following explains GitHub 'Pull Requests' feature:

    -https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests


    -https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request
