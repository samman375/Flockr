# Assumptions for COMP1531 Major Project
### by WED13Grape _– Team 4_


---

**Specific to auth functions:**

- First and last name can only contain a-z ascii characters, '_-_', and '_'_'
- First and last names can be duplicates of other first and last names (non-unique)
- Registering a new user automatically logs them in
- The first user registered is owner of the flockr
- Handlestrings can only contain characters from first and last name, with numbers (possibly) attached to end
- Numbers are added to handlestrings if non-unique names are used
- Emails must all conform to this expression/structure: `^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'`
- Password can contain any standard ascii characters
- There are no checks for password strength (other than password length)
- passwordreset/request raises InputError if invalid email provided
- Password cannot be same as previous password in passwordreset/reset

---

**Specific to channel functions:**

- Owners are included in list of all members
- User's requesting a list of members is included in the returned list
- A group is deleted when the last member leaves
- Ownership is transferred to the member with the next u_id
- Users cannot invite themselves or people already in a channel
- Timestamp for messages is stored in the format date_time
- There is no precedence in errors _(eg. InputError > AccessError)_
- The assumed working functions required to test channel_* functions are included in the comments at the beginning of each test file
- There must be at least 1 owner in a channel at any given time
- A flockr owner can access details of a channel even if they are not in it
- A flockr owner can join private channels

---

**Specific to channels functions:**

- User is automatically added to channel when it is created
- An empty string for channel name raises an InputError
- The channels_create() function will always generate a random & unique channel ID
- Channels are public by default
- A channel ID can be any length

---

**Specific to message functions:**

- When a message is edited to have no characters, it is deleted
- Owner of the flock or channel can edit and remove any message
- A message with zero characters will not be sent
- A user must be in the channel to edit or remove a message they sent
- Message IDs are generated through a counter that keeps track of how many messages have been sent in the entire flockr
- If a message is deleted, its ID cannot be reused
- More than one message can be pinned at a given time

---

**Specific to the search function:**

- The query string has no limit as to what characters can be inputted
- The query string only has to be _contained_ within a message for the message to be returned
- Search results are not case-specific

---

**Specific to the admin_userpermission_change function:**

- Flockr owners can change their own permission ID only if there's at least one flockr owner left after
- Setting the permission ID of a user to their current permission ID has no effect

---

**Specific to user/profile functions:**

- Users can only view their own details with user/profile
- Owners are not authorised to view other people's profiles
- x_start, y_start, x_end, y_end must be >= 0 in uploadphoto
