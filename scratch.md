S3 bucket name: foodiefriend-bucket

28/04
-made changes in navbar and added new template in templates for recs

-made changes in views for recs

-made changes in urls to add new recs page

==============================================================================================

todo:

==last==
-fb sign up - lucid
-change email functionality (need to send email validation)
-edit / save toggle functionality to update the forms on the front end
-your friend has invited you to socializer email
-create the page requestor to url param decorator
-new signup auth email (last)
==end==

==testing==
-make sure when users check each others profile, they should see only what they should see and can't do what they shouldn't (make sure they can't access stuff in the address bar of another profile)

-make sure when users check each others messages, they should see only what they should see and can't do what they shouldn't (make sure they can't access stuff in the address bar of another message profile)

-make sure when users check each others photos, they should see only what they should see and can't do what they shouldn't (make sure they can't access stuff in the address bar of another users photos)

-make sure when users check each others friends, they should see only what they should see and can't do what they shouldn't (make sure they can't access stuff in the address bar of another users photos)

-make sure when users check each others events, they should see only what they should see and can't do what they shouldn't (make sure they can't access stuff in the address bar of another users photos)

-make sure when users check each others notifications, they should see only what they should see and can't do what they shouldn't (make sure they can't access stuff in the address bar of another users photos)

-check if user needs to be logged in to access that resource first and then if it actually exisits - do this to make sure all 404s are handled

-test each app in iso
-==end==




git rm --cached */__pycache__/* - remove pycache from tracked files

==========================================================
today: (commit after each)

1. unfriend via friends page x
2. email form
3. change bell icon
4. get domain
5. get emails (no-reply and info) and adjust friend invite on profile
6. lots of errors are happening if a user without a profile is trying to view a profile page ie: line 106 on profile view. - do checks to handle gracefully





