S3 bucket name: foodiefriend-bucket

28/04
-made changes in navbar and added new template in templates for recs

-made changes in views for recs

-made changes in urls to add new recs page

==============================================================================================

todo:


-new signup auth email (last)


-change email functionality
-show / hide friend count
-change message implementation so people can't see each others messages page
-edit / save toggle functionality to update the forms on the front end
-make sure when users check each others profile, they should see only what they should see and can't do what they shouldn't (make sure they can't access stuff in the address bar of another profile)
-make sure when users check each others messages, they should see only what they should see and can't do what they shouldn't (make sure they can't access stuff in the address bar of another message profile)
-make sure when users check each others photos, they should see only what they should see and can't do what they shouldn't (make sure they can't access stuff in the address bar of another users photos)
-check if user needs to be logged in to access that resource first and then if it actually exisits - do this to make sure all 404s are handled
-create 10 fake users A - I, then do vigourous testing

git rm --cached */__pycache__/* - remove pycache from tracked files

==========================================================
today:

1. unauthorized messages inbox access x
2. BS login and signup forms
3. fix path for message notification x
4. when a user clicks on a notification, then that notification should be dismissed after the link is followed
5. make sure messages can be removed in message template

6. messages from reply interface in conversation view is not being marked as read correctly x
7. right time set to DMs x
8. notifications is currently doubled up in the url x
9. need to build out the friend page
10. outgoing messages should show in the senders messages page
11. fix categories (turn to albums) on photo page


