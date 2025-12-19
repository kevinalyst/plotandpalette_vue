The chart illustrates the data flow for a multi-step web application, detailing the interactions between the user, the frontend, and various backend services from the homepage to a final feedback form.

---

### **Homepage and Session Creation**

* The process begins on the **Homepage**, where the user submits a user information form.

* The frontend creates a session ID and sends it to the server; this session ID will be used whenever sending data to the database.

* The server then temporarily stores the session ID along with the user's name, age, gender, profession, and frequency before directing the user to the **Gradient palette page**.

---

### **Gradient Palette Page and API Interaction**

* On the **Gradient palette page**, the user clicks the "Capture" button.

* The frontend sends the name of the captured GIF to the server, which temporarily stores the GIF name.  
* The frontend saves the captured PNG to the uploads folder and sends the image path to the server, which in turn sends it to the **recommendation service**.

* The recommendation service performs several actions:

  * It gets raw extracted colours and mapped basic colours, both in RGB format.

  * It uses 85 colours features to create a features dataframe.  
  * It uses features to conduct similarity analyze and find the top 10 painting recommendations from the original data.

  * It sends the features to the **emotion predictions API**, which returns the 15 emotion predictions ranked by probabilities.

* The server sends the session\_id, top 10 painting recommendations, 15 emotion predictions ranked by probabilities to database \- API\_results table.  
* The server sends the captured image path, raw extracted colours(rgb), mapped basic colours(rgb), 15 emotion predictions ranked by probabilities to the frontend, colour palette page-emotion cards.  
* The server sends the top 10 painting recommendations to the frontend **Gallery page** \- gallery.  
* The frontend displays the **Colour palette page**, which includes the captured image, a raw colour section, a mapped colour section, and emotion cards.

* After the user selects an emotion card and clicks continue, the server temporarily stores the selected emotion.

---

### **Gallery, Story, and Feedback**

* On the **Gallery page**, the user drags and drops 3 paintings, selects a character, and inputs a nickname before clicking the "All done\!" button.   
* The session\_id, GIF name, selected emotion, three selected paintings URLs, selected character, and nickname are sent to the database-user\_behaviour table.

* The three selected paintings (title, artist, year, and URLs), the selected character, nickname, and selected emotion with probability are sent to the **secure story generator first,** then sent to the **Image story generator**. This generator creates a story title and text, which are displayed on the **Story page**.

* On the **Feedback page**, the user submits answers to Q1-Q15. This data, along with the temporarily stored session ID, user's name, age, gender, profession, and frequency, is sent to the database and stored in the **feedback table**.  
* Finally, clean the captured PNG from the uploads folder and clean any temporary stored data as well.  
