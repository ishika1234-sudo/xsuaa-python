# xsuaa-python
To show how to deploy python app in SAP Cloud Foundry, also, using XSUAA and HDI-DB services.
XSUAA- CF service used for authentication purpose. Only the authenticated users will be then allowed to use the application. Basically, it limits the access only to allowed users. 
HDI-DB/Container- HANA HDI-container to store users information and their uploads. 
User information is extracted by starting with a /login/callback url which performs the steps for fetching tokens using the authentication code. User is then redirected to the application home page. 
