S3 bucket name: foodiefriend-bucket

28/04
-made changes in navbar and added new template in templates for recs

-made changes in views for recs

-made changes in urls to add new recs page

==============================================================================================

todo:

==last==
-new signup auth email (last)
-change email functionality (need to send email validation)
-edit / save toggle functionality to update the forms on the front end
-add pagination to friends page
-make sure messages can be removed in message template
-outgoing messages should show in the senders messages page
-your friend has invited you to socializer email
==end==

==testing==
-make sure when users check each others profile, they should see only what they should see and can't do what they shouldn't (make sure they can't access stuff in the address bar of another profile)
-make sure when users check each others messages, they should see only what they should see and can't do what they shouldn't (make sure they can't access stuff in the address bar of another message profile)
-make sure when users check each others photos, they should see only what they should see and can't do what they shouldn't (make sure they can't access stuff in the address bar of another users photos)
-check if user needs to be logged in to access that resource first and then if it actually exisits - do this to make sure all 404s are handled
-==end==




git rm --cached */__pycache__/* - remove pycache from tracked files

==========================================================
today:

1. non logged in users should be able to browse an event
2. ability to remove albums with trash can - removes 
3. add remove button to individual images
4. mobile view for photos page
5. profile_id is set as url parameter
6. google social button is styled and google login is working
7. make sure get_object_or_404 is implemented accross apps
8. remove hi on HP for non-logged in users x
9. testing




. create 10 fake users A - I, then do vigourous testing



