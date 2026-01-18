# 01 – Prototyping Best Practices and Vibe Check

## 🏗️ Activity #1: General Vibe Checking Evals
1) Explain the concept of object-oriented programming in simple terms to a complete beginner.  
**Response:** Object-Oriented Programming (OOP) is a programming paradigm that uses "objects" to design software. Here are the key concepts in simple terms: 1. **Objects**: Think of objects as real-world things. Each object can have properties (attributes) and behaviors (methods). For example, a "Car" object might have properties like color and model, and behaviors like drive and stop. 2. **Classes**: A class is like a blueprint for creating objects. It defines what properties and behaviors the objects created from it will have. For example, you might have a class called "Car" that describes how all car objects should behave. 3. **Encapsulation**: This means keeping the details of how an object works hidden from the outside. You can interact with the object through its methods without needing to know how it does what it does. This helps protect the object's data. 4. **Inheritance**: This allows one class to inherit properties and methods from another class. For example, if you have a class "Vehicle," you could create a class "Car" that inherits from "Vehicle," meaning "Car" gets all the features of "Vehicle" plus any additional features specific to cars. 5. **Polymorphism**: This means that different classes can be treated as instances of the same class through a common interface. For example, if both "Car" and "Truck" classes have a method called "drive," you can call "drive" on both objects without needing to know which type of vehicle it is. In summary, OOP helps organize code in a way that makes it easier to manage, reuse, and understand by modeling real-world entities as objects.  
**Aspect Tested:**  

2) Read the following paragraph and provide a concise summary of the key points…  
**Response:** Recent advancements in artificial intelligence, particularly in Natural Language Processing, are enhancing the automated detection and prediction of mental health disorders. While deep learning methods have improved predictive accuracy, they often sacrifice model interpretability, which is crucial in healthcare. This work aims to fill the gap by systematically investigating explainable AI (XAI) approaches for detecting mental disorders through social media language behavior. The study involves building BiLSTM models using interpretable features related to language production and conducting experiments to balance accuracy and interpretability. Additionally, it compares these models with a pretrained transformer model and employs explanation techniques like LIME and AGRAD to identify key word categories influencing predictions. The approaches are tested on two public datasets covering five mental health conditions.  
**Aspect Tested:**  

3) Write a short, imaginative story (100–150 words) about a robot finding friendship in an unexpected place.  
**Response:** In a bustling city, a small retail company named Trendy Threads faced fierce competition from larger brands. To survive, they decided to harness the power of AI. By implementing an advanced analytics system, they analyzed customer purchasing patterns and preferences. This allowed them to personalize marketing campaigns, offering tailored promotions that resonated with individual shoppers. Additionally, they used AI-driven inventory management to predict trends and optimize stock levels, reducing waste and ensuring popular items were always available. As a result, Trendy Threads not only improved customer satisfaction but also increased sales significantly. Word spread about their innovative approach, attracting new customers and even partnerships with local designers. By embracing AI, Trendy Threads transformed from a struggling retailer into a market leader, proving that technology could level the playing field and create a sustainable competitive advantage.  
**Aspect Tested:**  

4) If a store sells apples in packs of 4 and oranges in packs of 3, how many packs of each do I need to buy to get exactly 12 apples and 9 oranges?  
**Response:** **Combinación de packs**: Vamos a probar diferentes combinaciones de packs para alcanzar al menos 230 cajas. - **Opción 1**: Usar solo Packs C. - Necesitamos 230 cajas. - 230 / 25 = 9.2 → 10 Packs C (250 cajas) - Costo: 10 * 32 € = 320 € - **Opción 2**: Usar 9 Packs C y complementar con Packs B. - 9 Packs C: 9 * 25 = 225 cajas - Necesitamos 5 cajas más. - 1 Pack B (14 cajas) es suficiente. - Total: 225 + 14 = 239 cajas - Costo: 9 * 32 € + 1 * 19 € = 288 € + 19 € = 307 € - **Opción 3**: Usar 8 Packs C y complementar con Packs B y A. - 8 Packs C: 8 * 25 = 200 cajas - Necesitamos 30 cajas más. - 2 Packs B (28 cajas) y 1 Pack A (6 cajas) = 34 cajas. - Total: 200 + 34 = 234 cajas - Costo: 8 * 32 € + 2 * 19 € + 1 * 9 € = 256 € + 38 € + 9 € = 303 € - **Opción 4**: Usar 7 Packs C y complementar. - 7 Packs C: 7 * 25 = 175 cajas - Necesitamos 55 cajas más. - 3 Packs B (42 cajas) y 2 Packs A (12 cajas) = 54 cajas. - Total: 175 + 54 = 229 cajas (no es suficiente). 3. **Conclusión**: La combinación más barata que permite obtener al menos 230 cajas es: - **9 Packs C** (250 cajas) - **1 Pack B** (14 cajas) - **Total de cajas**: 239 - **Costo mínimo**: 307 € Por lo tanto, la respuesta es: - Packs A: 0 - Packs B: 1 - Packs C: 9 - Total de cajas: 239 - Costo mínimo: 307 €  
**Aspect Tested:**  

5) Rewrite the following paragraph in a professional, formal tone…  
**Response:** I would like to inquire about the agenda for today's meeting. The discussion regarding 'strategic growth' became quite intense, which I found somewhat overwhelming. It might be beneficial for us to approach these topics with a more relaxed demeanor. On a lighter note, I was also contemplating the food I ordered.  
**Aspect Tested:**  

**❓Question #1:** Do the answers appear to be correct and useful?  
**✅ Answer:** No, not entirely. While the text-based responses (explanations, summaries, writing) are correct and useful, the mathematical reasoning response is incorrect, which makes that specific result misleading.  
Detailed Breakdown:  
Text & Language Tasks (Correct & Useful):  
OOP Explanation: Excellent. It simplifies complex concepts effectively.  
Summary: Accurate. It captures the main points of the abstract.  
Story: Good. It followed the prompt instructions well (even though your summary table mentions a "robot," the actual prompt asked for a story about "companies," and the model answered the prompt correctly).  
Tone Rewrite: Very good. It successfully converted a disrespectful, casual text into a professional email.  
Mathematical Logic Task (Incorrect):  
The Problem: The model failed to find the true mathematical optimization.  
The Model's Answer: It suggested 9 Packs C + 1 Pack B for a total of €307.  
The Correct Answer:  
9 Packs C (225 boxes) costs €288.  
You need 5 more boxes to reach 230.  
1 Pack A (6 boxes) costs €9.  
Total boxes: 231.  
Total Cost: €288 + €9 = €297.  
Conclusion: The model made you spend €10 more than necessary. It failed to check the combination of Pack C and Pack A, which is a common issue with LLMs (they are better at language than calculation/logic).  
Vibe Check Result:  
The model has a "High Verbal/Low Logic" vibe. It is trustworthy for drafting and summarizing but should not be trusted for calculation or optimization problems without human verification.  

---

## 🏗️ Activity #2: Personal Vibe Checking Evals (Your Assistant Can Answer)
**Prompt:** Help me design a 30 minute hands on exercise on RAG for EMBA students.  
**Result:** Certainly! Here’s a structured 30-minute hands-on exercise on Retrieval-Augmented Generation (RAG) for EMBA students: ### Exercise Title: **Exploring Retrieval-Augmented Generation (RAG)** #### Objective: To understand the concept of RAG and its application in enhancing information retrieval and generation processes. #### Materials Needed: - Laptops with internet access - Access to a RAG model (e.g., Hugging Face Transformers library) - Sample datasets (e.g., FAQs, product descriptions) - Whiteboard and markers for group discussions #### Exercise Outline: **1. Introduction (5 minutes)** - Briefly explain RAG: a model that combines retrieval and generation to provide more accurate and contextually relevant responses. - Discuss its applications in business, such as customer service, content creation, and data analysis. **2. Group Formation (2 minutes)** - Divide students into small groups of 3-4. **3. Hands-On Activity (15 minutes)** - **Step 1: Data Retrieval (5 minutes)** - Each group will access a provided dataset (e.g., a set of FAQs related to a specific industry). - Use a simple retrieval method (e.g., keyword search) to find relevant information based on a given query (e.g., "What are the benefits of our product?"). - **Step 2: Generating Responses (10 minutes)** - Using a RAG model (e.g., from Hugging Face), each group will input the retrieved information to generate a coherent response to the query. - Encourage groups to experiment with different queries and observe how the model's output changes based on the retrieved context. **4. Group Presentations (5 minutes)** - Each group presents their findings: - Share the query they used, the retrieved information, and the generated response. - Discuss any challenges faced and insights gained from the exercise. **5. Wrap-Up and Discussion (3 minutes)** - Facilitate a brief discussion on the implications of RAG in business contexts. - Ask students to reflect on how RAG can enhance decision-making and customer engagement. ### Conclusion: This exercise will provide EMBA students with practical experience in using RAG, fostering a deeper understanding of its potential in real-world applications.  

**Prompt:** Give me the pros and cons of using n8n vs. Make for automation in SMEs.  
**Result:** Certainly! Here’s a comparison of n8n and Make (formerly Integromat) for automation in small and medium-sized enterprises (SMEs): ### n8n **Pros:** 1. **Open Source**: n8n is open-source, allowing for customization and self-hosting, which can be more cost-effective and secure for SMEs. 2. **Flexibility**: It supports complex workflows and conditional logic, making it suitable for intricate automation needs. 3. **No Usage Limits**: There are no restrictions on the number of workflows or executions, which can be beneficial for growing businesses. 4. **Community Support**: A growing community provides resources, plugins, and support for users. **Cons:** 1. **Learning Curve**: The interface may be less intuitive for beginners compared to some other platforms, requiring more time to learn. 2. **Self-Hosting Complexity**: While self-hosting offers control, it also requires technical expertise and maintenance. 3. **Limited Built-in Apps**: While it has many integrations, it may not have as extensive a library of pre-built apps as some competitors. ### Make (Integromat) **Pros:** 1. **User-Friendly Interface**: Make offers a visual, drag-and-drop interface that is generally easier for non-technical users to navigate. 2. **Extensive Integrations**: It has a wide range of built-in apps and services, making it easy to connect various tools. 3. **Scenario-Based Automation**: Users can create complex scenarios with ease, including branching and error handling. 4. **Cloud-Based**: Being a cloud service, it requires no maintenance from the user’s side. **Cons:** 1. **Cost**: Make operates on a subscription model, which can become expensive as usage scales up, especially for SMEs with tight budgets. 2. **Execution Limits**: Plans come with limits on the number of operations and data transfer, which may hinder larger automation needs. 3. **Less Customization**: While it’s user-friendly, it may not offer the same level of customization as an open-source solution like n8n. ### Conclusion The choice between n8n and Make depends on your SME's specific needs. If you prioritize customization, control, and cost-effectiveness, n8n may be the better option. If ease of use and extensive integrations are more critical, Make could be the way to go.  

**Prompt:** Subject: Proposal for Update on Digital Transformation Program Dear Stanpa Team, I hope this message finds you well. I am writing to propose an update to our ongoing digital transformation program. As we continue to adapt to the evolving market landscape, I believe it is essential to assess our current strategies and explore new opportunities that can enhance our efficiency and customer engagement. I suggest we schedule a meeting to discuss potential areas for improvement, including the integration of new technologies, process optimization, and data analytics. This collaborative effort will ensure that we remain at the forefront of innovation and can better serve our stakeholders. Please let me know your availability for a meeting in the coming weeks. I look forward to your feedback and to working together on this important initiative. Best regards, [Your Name] [Your Position] [Your Contact Information] [Your Company]  
**Result:**  

**❓Question #2:** Are the vibes of this assistant's answers aligned with your vibes? Why or why not?  
**✅ Answer:** No, the assistant's "vibe" is NOT currently aligned with me.  
Why?  
While the model is polite and grammatically correct, it behaves like a generic search engine rather than a strategic executive assistant. It lacks the necessary context about who you are (a professor/consultant) and fails to adapt to your specific audience.  
Here is the breakdown of why the alignment is off:  
The EMBA Context Failure (Critical Mismatch):  
The model suggested that EMBA students (executives/managers) use the "Hugging Face Transformers library" in a 30-minute session.  
Why this fails: This is technically unrealistic and pedagogically wrong. EMBA students focus on strategy, not Python coding. A model aligned with your vibe would have suggested a high-level conceptual exercise or a no-code tool, not a developer library. It understands the tech but not the business context.  
The Email Hallucination (Lack of Caution):  
The model invented a "Digital Transformation Program" out of thin air.  
Why this fails: A trusted personal assistant does not invent facts. It should have used clear placeholders (e.g., [Insert Project Name]) or asked you for the specific topic before drafting. By making things up, it forces you to spend more time correcting it than if you had written it yourself.  
The n8n vs. Make Comparison (Generic):  
The response was accurate but "encyclopedic." It listed facts without analyzing which one fits your specific situation (e.g., "Do you have a dev team? Use n8n. Are you a solo founder? Use Make").  
The model currently has a "Junior Analyst" vibe—it knows facts but lacks judgment. To align with your vibe, it needs more context (System Prompts) to understand that you need strategic, executive-level outputs, not generic or overly technical ones.  

---

## 🏗️ Activity #3: Personal Vibe Checking Evals (Requires Additional Capabilities)
**Prompt:** What does my schedule look like tomorrow?  
**Result:** I'm sorry, but I don't have access to your personal schedule. You can check your calendar app or planner for your appointments and tasks for tomorrow. If you need help organizing your schedule, feel free to ask!  

**Prompt:** What time should I leave for the airport?  
**Result:** To determine what time you should leave for the airport, consider the following factors: 1. **Flight Departure Time**: Check your flight's departure time. 2. **Airport Arrival Time**: Aim to arrive at least 2-3 hours before a domestic flight and 3-4 hours before an international flight. 3. **Travel Time to the Airport**: Calculate how long it takes to get to the airport, including potential traffic. 4. **Security and Check-in**: Factor in time for check-in and security checks. For example, if your flight is at 3 PM, and you need to be at the airport by 1 PM, and it takes you 30 minutes to get there, you should leave by 12:30 PM. Adjust based on your specific circumstances.  

**❓Question #3:** What are some limitations of your application?  
**✅ Answer:** The primary limitation is that the application operates in isolation (a "sandbox") and lacks integration with your personal data sources.  
Here is a breakdown of the specific limitations revealed by these prompts:  
No Access to Personal Data (The "Calendar" Problem):  
The model cannot answer "What does my schedule look like?" because it is not connected to my Outlook. It does not have permission to read my private database.  
Lack of Real-Time Context (The "Airport" Problem):  
The model gave a generic "rule of thumb" answer because it lacks three critical pieces of real-time information:  
Location: It doesn't know where I am located.  
Traffic: It cannot check Google Maps for current travel times.  
Flight Status: It cannot verify if your flight is delayed.  
Zero "State" Awareness:  
Unlike a true personal assistant (like Siri or a human secretary), this LLM does not remember my habits or previous contexts unless they are currently in the chat window. It treats every question as a generic query rather than a personalized task.  
Currently, the application is a reasoning engine, not a doer. To be useful as a personal assistant, it would need "Function Calling" capabilities or access to Plugins that allow it to read my calendar and check live traffic.  

---

## Executive Summary
This evaluation assesses the AI assistant's readiness for professional use across three dimensions:  
1. Baseline Functionality (Activity 1): The application demonstrates strong capabilities in Natural Language Processing, excelling at summarization, tone adjustment, and conceptual explanation. However, it fails in mathematical reasoning and optimization, meaning it cannot be trusted with calculation-heavy tasks without human verification.  
2. Strategic Fit (Activity 2): The assistant is currently misaligned with the user’s executive profile. It defaults to a "generic encyclopedia" persona—suggesting overly technical solutions for management students and hallucinating details in drafts—rather than acting as a context-aware professional partner.  
3. System Limitations (Activity 3): The application operates in isolation. Its inability to access personal data (calendars) or real-time variables (traffic, flight status) confirms it acts as a reasoning engine rather than an integrated personal assistant.  

---

## 🚧 Advanced Build (OPTIONAL)
**Adjustments Made:**  
(describe adjustment(s) here)

**Results:**  
(Comment here how the change(s) impacted the vibe check of your system)

---

## Submission
- GitHub repo URL:  
- Vercel public URL (Challenge project):  
