# FacebookSSOCrawler

Description:
FacebookSSOCrawler.py is a script that crawls through a provided list of websites that potentially have Facebook as a Single-Sign on provider. After it visits each site, it attempts to find and click any Faebook SSO registration buttons. If a button is correctly identified and successfully clicked, it then collects the list of permissions for the user's personal Faceboook data that the site is requesting to access. The output is a CSV file with the crawl results (either button was found and permissions are available, or button was not found). The goal was to identify trends in the number and frequency of types of permissions asked.

FacebookSSOCrawler_v2.py is an update to FacebookSSOCrawler that allows for the site crawl list file name and facebook login credentials to be dynamically entered as run time arguments.

Running the crawlers:
To run FacebookSSOCrawler_v2.py, use the command: "python FacebookSSOCrawler_v2.py ./file_name.txt  email_address password", where file_name.txt is the path to/name of the file containing the lists of sites to crawl, and email_address and password correspond to the account credentials to be used to log into Facebook. The output is two csv files "crawlResults_CSV.txt" and crawlResultsCSV_temp.txt". The final file contains the full dataset and final program runtime.

To run the FacebookSSOCrawler, you must have both Selenium and geckodriver (Mozilla web driver) installed. The file with the list of sites to crawl should be in the same directory as the script or the path should be specified when setting the file variable. Before running the program, you must change the contents of the json_file variable in line 24 to be the file name of the file containing the sites that are wished to crawl. For example, if the sites are contained in a file named "FirstHundred.txt", then this would be 
json_file = "FirstHundred.txt" The same must be done for the variables user (line 87) and pwd (line 88). These variables are used to specify the login credentials for the Facebook account that is logged into during the crawl (which allows the permissions list to be easily obtained). user should be set to a string containing the Facebook account email, and pwd should be a string containing the account password. For example:
user = "email@email.com"
pwd = "facebook password"
After these variables have been updated, the program may be run as any other python script with the command "python FacebookSSOCrawler.py" The script will output two csv formatted files named "retest_CSV.txt" and "retestCSV_temp.txt". These files contain the rank of the domain crawled, the last site that was crawled for that domain, the url that the Facebook permissions were identified on, the number of permissions requested, and finally an explicit a list of the permissions requested. The temp file is written to as the program is running in case of a crash.

Other included files:

FinalDataset.cv
This is the final dataset that was obtained from a crawl of the first 2000 lists of sites (for first 2000 top ranked sites containing Facebook sso registration among the Alexa top 1M) form the originating study's JSON dataset. study and original dataset can be found here: https://www.cs.uic.edu/~sso-study/

FirstOneHundred.txt
This is the first 100 sites from the JSON dataset reformatted to be loadable into python as JSON data. If used to run a crawler script, it will return results for the top 100 sites identified as having Facebook SSO.

fullFacebookSSODataset_toCrawl.txt
This file contains the entire list of 43,333 domains and corresponding site lists identified as having Facebook SSO. it is formatted to run with the crawler scripts.

ssoFacebookFirst2000.txt
This is the full list of site lists that were crawled for our semester project research study. It is also formatted to run correctly with the crawler scripts. 

This project was made possible by the work of Mohammad Ghasemisharif, Amrutha Ramesh, Stephen Checkoway, Chris Kanich, and Jason Polakis at the University of Illinois at Chicago and their study "An Empirical Analysis of Single Sign-On Account Hijacking and Session Management on the Web" [1]. Their original study and datasets that were utilized in this study can be found here: https://www.cs.uic.edu/~sso-study/

References
[1] Mohammad Ghasemisharif, Amrutha Ramesh, Stephen Check-oway, Chris Kanich, and Jason Polakis. O Single Sign-Off, WhereArt Thou? An Empirical Analysis of Single Sign-On Account Hi-jacking and Session Management on the Web . In Proceedingsof the 27th USENIX Security Symposium. Baltimore, MD, USA.https://www.cs.uic.edu/ polakis/papers/sso-usenix18.pdf
