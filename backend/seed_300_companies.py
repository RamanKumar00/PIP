import sys
import os
import uuid
from datetime import datetime, timezone

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal, Base, engine
from app.models.company import Company, CompanyRole, EligibilityRule, CompanySkillWeight

# Detailed templates for Indian-specific and global industries to make the data highly realistic
ROLE_TEMPLATES = {
    "IT Services": {
        "title": "Associate Software Engineer (ASE)",
        "description": "Provide software development, testing, and cloud infrastructure support for global enterprise clients. Participate in agile sprint cycles, resolve production tickets, and assist in legacy codebase migrations.",
        "hiring_pattern": "Cognitive & Technical Assessment (Aptitude, Pseudocode, Common Applications) followed by a Technical Interview (Coding, DBMS, OOP) and a final HR / Managerial discussion.",
        "expected_oa_pattern": "MCQs on quantitative aptitude, logical reasoning, verbal ability, pseudocode debugging, and 1 easy coding challenge (e.g. String reverse or Array search).",
        "technical_interview_topics": ["Core Java", "SQL", "Object-Oriented Programming", "HTML & CSS", "Aptitude"],
        "hr_interview_topics": ["Communication Skills", "Relocation Flexibility", "Shift Adaptability", "Teamwork"],
        "interview_experience": "A candidate shared: 'The technical round was friendly. They asked me about my final year project, basic SQL joins, and differences between list and set in Java. The HR round focused on relocations and shift flexibilities.'",
        "preparation_resources": ["TCS NQT Preparation Guide", "GeeksforGeeks placement preparation", "Java Programming Basics"]
    },
    "IT Consulting": {
        "title": "Technology Consultant",
        "description": "Engage with clients to analyze business requirements, design software integration blueprints, and deploy CRM/ERP enterprise solutions. Assist in system integration and technical risk analysis.",
        "hiring_pattern": "Online Technical test (SQL, DSA, Aptitude) followed by a Case Study/Group Discussion, 1 Technical Interview, and a Managerial interview.",
        "expected_oa_pattern": "30 MCQs on database queries, Excel formulations, logical reasoning, and 1 easy-medium coding problem.",
        "technical_interview_topics": ["SQL Queries", "Relational Databases", "Systems Integration", "Excel & Analytics", "SDLC Methodologies"],
        "hr_interview_topics": ["Problem Solving", "Client Communication", "Adaptability", "Presentation Skills"],
        "interview_experience": "A candidate shared: 'They gave me a business scenario (e.g. migration of billing databases) and asked me to write SQL queries to extract active accounts. The focus was on analytical thinking.'",
        "preparation_resources": ["SQL Practice Set", "Consulting Case Study Prep", "SDLC Lifecycle Essentials"]
    },
    "FinTech": {
        "title": "Software Engineer - Payments Backend",
        "description": "Design and optimize high-throughput transaction processing systems, ledger databases, and secure payment gateway APIs. Ensure 99.99% system uptime, low latency, and PCI-DSS compliance.",
        "hiring_pattern": "Online Coding Assessment (2 API/system-related DSA questions) followed by 1 Systems Design Round (Ledger/Wallet architecture) and 2 Technical Rounds focusing on databases, concurrency, and caching.",
        "expected_oa_pattern": "2 coding questions focusing on transaction concurrency, rate limiters, or array/string manipulation.",
        "technical_interview_topics": ["System Design", "Databases", "Concurrency", "Redis Caching", "REST APIs"],
        "hr_interview_topics": ["Problem Solving", "Conflict Resolution", "Ownership", "Code Quality Standards"],
        "interview_experience": "A candidate reported: 'They asked me to design a simplified digital wallet ledger system handling concurrent requests. The questions focused heavily on transaction isolation levels and database locking mechanisms.'",
        "preparation_resources": ["Designing Data-Intensive Applications", "System Design Primer", "LeetCode Concurrency Problems"]
    },
    "E-Commerce & Retail": {
        "title": "Software Development Engineer (SDE-1)",
        "description": "Develop high-scale catalog search, pricing algorithms, real-time inventory tracking, and order dispatch services. Optimize checkout latency, caching strategies, and search relevancy.",
        "hiring_pattern": "Online coding challenge (2 DSA questions) followed by a machine coding round (design and implement a working class/library under 90 minutes) and 2 technical rounds (DSA + system design).",
        "expected_oa_pattern": "2 medium/hard DSA questions focusing on priority queues, dynamic programming, or graphing algorithms.",
        "technical_interview_topics": ["Data Structures", "Algorithms", "Object-Oriented Design", "System Design", "Caching"],
        "hr_interview_topics": ["Customer Centricity", "Ownership", "Bias for Action", "Collaboration"],
        "interview_experience": "A candidate reported: 'The machine coding round required implementing an order delivery allocation system. They checked coding clean standards, SOLID principles, and working execution.'",
        "preparation_resources": ["Clean Code by Robert Martin", "LeetCode Priority Queue Problems", "Grokking the Machine Coding Interview"]
    },
    "E-Commerce & Delivery": {
        "title": "SDE-1 (Logistics & Routing)",
        "description": "Engineer low-latency routing algorithms, driver dispatch services, and live ETA tracking APIs. Optimize geospatial queries and spatial data pipelines under heavy traffic conditions.",
        "hiring_pattern": "Online DSA coding challenge followed by 1 Machine Coding round (Low-level design of dispatch/matching logic) and 2 Technical DSA/System rounds.",
        "expected_oa_pattern": "2 medium DSA problems focusing on Graph traversals (Dijkstra, BFS) and heap data structures.",
        "technical_interview_topics": ["Algorithms", "Geospatial Indexing", "System Design", "Concurrency", "Redis"],
        "hr_interview_topics": ["Customer Obsession", "Speed of Execution", "Handling Pressures", "Culture Fit"],
        "interview_experience": "A candidate shared: 'The interview focused on Dijkstra's algorithm variant to assign delivery boys to partners. They checked my low-level design classes and memory complexity.'",
        "preparation_resources": ["Graph Algorithms Guide", "Low-Level Design Patterns", "GeeksforGeeks Machine Coding Examples"]
    },
    "Technology": {
        "title": "Software Development Engineer (SDE)",
        "description": "Engineer core cloud infrastructure, distributed microservices, and high-performance algorithms. Focus on web-scale system architecture, developer platform tools, and codebase clean-ups.",
        "hiring_pattern": "Online Coding Test followed by 3 Technical Rounds (DSA, System Architecture, Code Design) and 1 Culture Fitment Round.",
        "expected_oa_pattern": "2 algorithmic coding questions (medium-hard difficulty) on tree/graph traversals, advanced dynamic programming, or segment trees.",
        "technical_interview_topics": ["Data Structures", "Algorithms", "System Design", "Distributed Systems", "Operating Systems"],
        "hr_interview_topics": ["Growth Mindset", "Inclusion", "Leadership Traits", "Collaboration"],
        "interview_experience": "A candidate shared: 'The DSA questions were quite challenging and based on trie structures and graph coloring. The system design round focused on building a globally distributed rate-limiting service.'",
        "preparation_resources": ["LeetCode Top 100 Liked", "Alex Xu System Design Volume 1 & 2", "GitHub System Design Primer"]
    },
    "SaaS & Cloud": {
        "title": "Software Engineer - Cloud Systems",
        "description": "Develop multi-tenant SaaS application backends, cloud orchestration pipelines, and robust developer APIs. Optimize query latency, memory caching, and database indexing.",
        "hiring_pattern": "Online Coding Assessment followed by 2 Technical rounds (DSA + Database design) and 1 System design/API design interview.",
        "expected_oa_pattern": "2 coding questions (easy-medium) focusing on string manipulation, hash maps, and relational database schema queries.",
        "technical_interview_topics": ["REST APIs", "DBMS & SQL", "Cloud Storage (AWS/Azure)", "Caching", "Git & CI/CD"],
        "hr_interview_topics": ["Customer Obsession", "Attention to Detail", "Quality-First Mindset", "Growth"],
        "interview_experience": "A candidate shared: 'They asked me to write clean REST API specifications for a document collaborative system. They focused on HTTP status codes, caching headers, and database relationships.'",
        "preparation_resources": ["REST API Design Best Practices", "High Performance MySQL", "LeetCode Database Questions"]
    },
    "Investment Banking": {
        "title": "Analyst - Core Technology",
        "description": "Develop high-frequency trading platforms, risk analytics engines, and secure transaction systems. Focus on multi-threading, concurrency, memory optimization, and garbage collection tuning.",
        "hiring_pattern": "Online Test (Coding, Math, Finance basics) followed by 3 technical rounds focusing on OOP, concurrency, system internals, and SQL.",
        "expected_oa_pattern": "2 coding problems on arrays/graphs and 20 MCQs on OS internals, memory management, and databases.",
        "technical_interview_topics": ["Java Concurrency", "Memory Internals", "C++ Optimizations", "SQL & Indexing", "Operating Systems"],
        "hr_interview_topics": ["Integrity", "Performance under Stress", "Analytical Thinking", "Ethics"],
        "interview_experience": "A candidate shared: 'They asked very deep questions on Java garbage collection, volatile variables, and multi-threading deadlock situations. Make sure you know OS internals and database transactions.'",
        "preparation_resources": ["Java Concurrency in Practice", "Operating System Concepts by Galvin", "LeetCode Core DSA"]
    },
    "Commercial Banking": {
        "title": "Associate IT Analyst",
        "description": "Support and develop retail banking platforms, credit risk assessment modules, and digital wallet APIs. Maintain secure codebases and legacy integrations.",
        "hiring_pattern": "Online assessment (Aptitude + Basic coding) followed by 2 technical rounds (SQL, Java/C#, basics of web) and 1 managerial interview.",
        "expected_oa_pattern": "20 MCQs on logical aptitude, SQL basics, and 1 easy coding problem (e.g. bubble sort or palindrome).",
        "technical_interview_topics": ["Core Java / C#", "SQL Queries", "Relational Database Basics", "SDLC", "Web Basics"],
        "hr_interview_topics": ["Team Player", "Integrity", "Adaptability", "Long-term commitment"],
        "interview_experience": "A candidate shared: 'The interview focused on writing basic SQL joins, aggregate functions, and HTML form validation. The HR round was standard behavioral questions.'",
        "preparation_resources": ["SQL Zoo", "Java Beginners Guide", "Basic Web Development Practice"]
    },
    "Automotive": {
        "title": "Embedded Systems Engineer",
        "description": "Develop and test ECU firmware, sensor integration modules, and CAN bus communication protocols. Optimize memory footprint and safety-critical threads.",
        "hiring_pattern": "Online test (Embedded C, electronics, basic coding) followed by 2 technical interviews (microcontrollers, Embedded C, circuit design) and 1 HR round.",
        "expected_oa_pattern": "15 MCQs on electronics/C basics and 1 low-level bit manipulation coding problem.",
        "technical_interview_topics": ["Embedded C", "Microcontrollers", "CAN Bus Protocol", "Bitwise Operators", "RTOS Concepts"],
        "hr_interview_topics": ["Attention to Detail", "Safety Mindset", "Teamwork", "Problem Solving"],
        "interview_experience": "A candidate reported: 'They asked me to write a C function to reverse bits in a byte without using helper variables. They also checked my understanding of interrupt service routines (ISRs).'",
        "preparation_resources": ["Embedded C Programming", "RTOS Basics Guide", "LeetCode Bit Manipulation Study Plan"]
    },
    "Gaming": {
        "title": "Gameplay Programmer",
        "description": "Design and develop game mechanics, physics simulation engines, and graphics rendering pipelines. Optimize frame rates, CPU memory, and asset loading threads.",
        "hiring_pattern": "Online coding challenge (C++ & Math) followed by 2 technical rounds (C++, Linear Algebra, game loop logic) and 1 portfolio review.",
        "expected_oa_pattern": "2 coding problems in C++ on vector mathematics, collision detection, or pathfinding (A*).",
        "technical_interview_topics": ["C++ Programming", "Linear Algebra & Vectors", "Game Engine Architecture", "Memory Management", "Unreal Engine / Unity"],
        "hr_interview_topics": ["Creative Thinking", "Passion for Gaming", "Collaboration", "Handling Deadlines"],
        "interview_experience": "A candidate shared: 'They checked my knowledge of C++ pointers, virtual tables, and memory fragmentation. They also asked me to write vector projection code on the whiteboard.'",
        "preparation_resources": ["C++ Primer by Lippman", "Linear Algebra for Game Developers", "Game Engine Architecture by Jason Gregory"]
    },
    "Telecom": {
        "title": "Network Software Engineer",
        "description": "Develop and maintain high-bandwidth network protocols, VoIP services, and telecommunication databases. Optimize data packet parsing and network concurrency.",
        "hiring_pattern": "Online test (Network basics, Unix commands, coding) followed by 2 technical rounds (Socket programming, C/C++, OS) and 1 HR fitment.",
        "expected_oa_pattern": "20 MCQs on TCP/IP protocols, subnetting, Unix commands, and 1 easy-medium coding problem.",
        "technical_interview_topics": ["TCP/IP Networking", "Socket Programming", "Unix/Linux Systems", "C/C++", "Multithreading"],
        "hr_interview_topics": ["Collaboration", "Analytical Skills", "Customer Orientation", "Communication"],
        "interview_experience": "A candidate shared: 'The interviewer asked me to explain the TCP handshake in detail and write a basic client-server socket program in C. OS concepts like processes vs threads were also tested.'",
        "preparation_resources": ["Computer Networks by Tanenbaum", "Unix Network Programming", "LeetCode Networking Prep"]
    },
    "Healthcare": {
        "title": "Bioinformatics Software Analyst",
        "description": "Develop data analytics pipelines for clinical trial results, patient records databases, and image processing tools. Ensure data privacy and compliance.",
        "hiring_pattern": "Online test (Data analysis, SQL, Python) followed by 2 technical interviews (Python data libraries, SQL, algorithms) and 1 HR manager round.",
        "expected_oa_pattern": "20 MCQs on statistics/data query, and 1 Python coding challenge on data sanitization.",
        "technical_interview_topics": ["Python (Pandas, Numpy)", "SQL Database Queries", "Data Security", "Statistics", "Git"],
        "hr_interview_topics": ["Ethical Standards", "Compliance Focus", "Problem Solving", "Detail Orientation"],
        "interview_experience": "A candidate shared: 'They checked my Python data processing skills using Pandas. They asked how to handle missing data columns in patient records. Database query optimization was also key.'",
        "preparation_resources": ["Python Data Science Handbook", "SQL Zoo Practice", "HIPAA Data Privacy Guidelines"]
    },
    "EdTech": {
        "title": "Frontend Engineer - Learning Platforms",
        "description": "Design and build interactive student dashboards, video streaming widgets, and assessment portal interfaces. Ensure responsiveness, accessibility, and fast load times.",
        "hiring_pattern": "Online UI coding challenge followed by 2 technical rounds (JavaScript, CSS, React components, web optimizations) and 1 HR discussion.",
        "expected_oa_pattern": "Create an interactive interface component (like a search filter or video player UI) within 90 minutes.",
        "technical_interview_topics": ["JavaScript / TypeScript", "React Framework", "HTML5 & CSS3", "Web Performance", "State Management (Redux)"],
        "hr_interview_topics": ["User Empathy", "Creative Design", "Adaptability", "Growth Mindset"],
        "interview_experience": "A candidate shared: 'They asked me to build a custom React course listing grid component with pagination and search filtering. They graded on clean DOM elements, CSS styles, and accessibility.'",
        "preparation_resources": ["JavaScript Info", "React Official Docs Guide", "Web.dev Performance Optimizations"]
    }
}

# The base company list from the previous seeder
COMPANIES_DATA = [
    # 1. Technology / FANG / Product Giants (30 companies)
    ("Google", "https://google.com", "Technology", "Mountain View, CA", 35.0, "Hard", ["CSE", "IT", "ECE"], 8.5, [("Python", 5, "Expert"), ("C++", 5, "Expert"), ("Git", 4, "Intermediate")]),
    ("Amazon", "https://amazon.jobs", "Cloud & E-Commerce", "Seattle, WA", 28.5, "Hard", ["CSE", "IT", "ECE", "EEE"], 8.0, [("FastAPI", 4, "Intermediate"), ("PostgreSQL", 5, "Intermediate"), ("AWS", 5, "Intermediate")]),
    ("Microsoft", "https://careers.microsoft.com", "Technology", "Redmond, WA", 24.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("C++", 5, "Intermediate"), ("React", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Meta", "https://careers.meta.com", "Technology", "Menlo Park, CA", 42.0, "Hard", ["CSE", "IT"], 8.5, [("Python", 5, "Expert"), ("React", 5, "Expert"), ("Docker", 4, "Intermediate")]),
    ("Netflix", "https://jobs.netflix.com", "Technology", "Los Gatos, CA", 45.0, "Hard", ["CSE", "IT"], 8.5, [("Java", 5, "Expert"), ("Kafka", 5, "Expert"), ("Docker", 5, "Expert")]),
    ("Apple", "https://www.apple.com/careers", "Technology", "Cupertino, CA", 38.0, "Hard", ["CSE", "IT", "ECE"], 8.0, [("Swift", 5, "Expert"), ("C++", 5, "Expert"), ("Git", 4, "Intermediate")]),
    ("Tesla", "https://www.tesla.com/careers", "Automotive", "Austin, TX", 26.0, "Hard", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.5, [("Python", 4, "Intermediate"), ("C++", 5, "Expert"), ("Git", 4, "Intermediate")]),
    ("Uber", "https://www.uber.com/careers", "Technology", "San Francisco, CA", 32.0, "Hard", ["CSE", "IT", "ECE"], 8.0, [("Go", 5, "Expert"), ("Java", 4, "Intermediate"), ("Redis", 4, "Intermediate")]),
    ("Salesforce", "https://careers.salesforce.com", "SaaS & Cloud", "San Francisco, CA", 22.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("JavaScript", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Adobe", "https://www.adobe.com/careers", "Technology", "San Jose, CA", 25.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("C++", 5, "Expert"), ("Java", 4, "Intermediate"), ("JavaScript", 4, "Intermediate")]),
    ("Spotify", "https://www.lifeatspotify.com", "Technology", "Stockholm, Sweden", 24.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Kafka", 4, "Intermediate")]),
    ("Twitter", "https://careers.twitter.com", "Technology", "San Francisco, CA", 20.0, "Medium", ["CSE", "IT"], 7.5, [("Scala", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("Redis", 4, "Intermediate")]),
    ("Stripe", "https://stripe.com/jobs", "FinTech", "San Francisco, CA", 36.0, "Hard", ["CSE", "IT"], 8.0, [("Ruby", 5, "Expert"), ("Go", 4, "Intermediate"), ("REST APIs", 5, "Expert")]),
    ("Airbnb", "https://careers.airbnb.com", "Technology", "San Francisco, CA", 30.0, "Hard", ["CSE", "IT"], 8.0, [("Java", 4, "Intermediate"), ("React", 5, "Expert"), ("Ruby", 4, "Intermediate")]),
    ("Dropbox", "https://www.dropbox.com/jobs", "Technology", "San Francisco, CA", 28.0, "Medium", ["CSE", "IT"], 7.5, [("Python", 5, "Expert"), ("Go", 4, "Intermediate"), ("Rust", 4, "Intermediate")]),
    ("Zoom", "https://careers.zoom.us", "Technology", "San Jose, CA", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("C++", 5, "Intermediate"), ("Java", 4, "Intermediate"), ("Nginx", 4, "Intermediate")]),
    ("Slack", "https://slack.com/careers", "SaaS & Cloud", "San Francisco, CA", 22.0, "Medium", ["CSE", "IT"], 7.5, [("React", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Figma", "https://www.figma.com/careers", "Technology", "San Francisco, CA", 30.0, "Hard", ["CSE", "IT"], 8.0, [("TypeScript", 5, "Expert"), ("React", 4, "Intermediate"), ("C++", 4, "Intermediate")]),
    ("LinkedIn", "https://careers.linkedin.com", "Technology", "Sunnyvale, CA", 26.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("Java", 5, "Expert"), ("Python", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("PayPal", "https://careers.pypl.com", "FinTech", "San Jose, CA", 20.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("Java", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("ByteDance", "https://jobs.bytedance.com", "Technology", "Beijing, China", 38.0, "Hard", ["CSE", "IT", "ECE"], 8.0, [("Go", 5, "Expert"), ("Python", 4, "Intermediate"), ("Redis", 4, "Intermediate")]),
    ("Oracle", "https://careers.oracle.com", "SaaS & Cloud", "Austin, TX", 18.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("Java", 5, "Expert"), ("SQL", 5, "Expert"), ("Linux", 4, "Intermediate")]),
    ("NVIDIA", "https://www.nvidia.com/careers", "Technology", "Santa Clara, CA", 36.0, "Hard", ["CSE", "IT", "ECE", "EEE"], 8.5, [("C++", 5, "Expert"), ("Python", 4, "Intermediate"), ("Docker", 4, "Intermediate")]),
    ("Intel", "https://jobs.intel.com", "Technology", "Santa Clara, CA", 16.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Bash", 4, "Intermediate")]),
    ("AMD", "https://careers.amd.com", "Technology", "Santa Clara, CA", 18.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("C++", 5, "Intermediate"), ("Python", 4, "Intermediate"), ("Verilog", 4, "Intermediate")]),
    ("Qualcomm", "https://www.qualcomm.com/careers", "Technology", "San Diego, CA", 17.5, "Medium", ["ECE", "CSE", "EEE"], 7.5, [("C", 5, "Expert"), ("C++", 4, "Intermediate"), ("Python", 4, "Intermediate")]),
    ("Cisco", "https://jobs.cisco.com", "Technology", "San Jose, CA", 16.5, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("Python", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("Nginx", 4, "Intermediate")]),
    ("IBM", "https://www.ibm.com/employment", "IT Services", "Armonk, NY", 14.0, "Medium", ["CSE", "IT", "ECE", "EEE", "MECH"], 7.0, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Docker", 4, "Intermediate")]),
    ("HP", "https://jobs.hp.com", "Technology", "Palo Alto, CA", 12.0, "Easy", ["CSE", "IT", "ECE", "MECH"], 7.0, [("C++", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Dell", "https://jobs.dell.com", "Technology", "Round Rock, TX", 12.5, "Easy", ["CSE", "IT", "ECE", "MECH"], 7.0, [("C#", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Windows Server", 4, "Intermediate")]),

    # 2. FinTech, Payments & Crypto (40 companies)
    ("Adyen", "https://careers.adyen.com", "FinTech", "Amsterdam, Netherlands", 25.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate"), ("REST APIs", 4, "Intermediate")]),
    ("Klarna", "https://careers.klarna.com", "FinTech", "Stockholm, Sweden", 24.0, "Medium", ["CSE", "IT"], 7.5, [("TypeScript", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Plaid", "https://plaid.com/careers", "FinTech", "San Francisco, CA", 32.0, "Hard", ["CSE", "IT"], 8.0, [("TypeScript", 4, "Intermediate"), ("Go", 4, "Intermediate"), ("REST APIs", 5, "Expert")]),
    ("Robinhood", "https://careers.robinhood.com", "FinTech", "Menlo Park, CA", 34.0, "Hard", ["CSE", "IT"], 8.0, [("Python", 5, "Intermediate"), ("Go", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Coinbase", "https://www.coinbase.com/careers", "FinTech", "San Francisco, CA", 35.0, "Hard", ["CSE", "IT"], 8.0, [("Go", 4, "Intermediate"), ("Ruby", 4, "Intermediate"), ("Docker", 4, "Intermediate")]),
    ("Binance", "https://www.binance.com/en/careers", "FinTech", "Malta", 28.0, "Hard", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("Go", 4, "Intermediate"), ("Redis", 4, "Intermediate")]),
    ("Kraken", "https://careers.kraken.com", "FinTech", "San Francisco, CA", 26.0, "Medium", ["CSE", "IT"], 7.5, [("Rust", 4, "Intermediate"), ("PHP", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Revolut", "https://www.revolut.com/careers", "FinTech", "London, UK", 25.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Monzo", "https://monzo.com/careers", "FinTech", "London, UK", 22.0, "Medium", ["CSE", "IT"], 7.5, [("Go", 4, "Intermediate"), ("Cassandra", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Wise", "https://wise.jobs", "FinTech", "London, UK", 20.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("Spring Boot", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("N26", "https://n26.com/en-de/careers", "FinTech", "Berlin, Germany", 18.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("Spring Boot", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Chime", "https://chime.com/careers", "FinTech", "San Francisco, CA", 28.0, "Medium", ["CSE", "IT"], 7.5, [("Ruby", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("SoFi", "https://www.sofi.com/careers", "FinTech", "San Francisco, CA", 24.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Kotlin", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Razorpay", "https://razorpay.com/jobs", "FinTech", "Bengaluru, India", 18.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("PHP", 4, "Intermediate"), ("Go", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Paytm", "https://careers.paytm.com", "FinTech", "Noida, India", 12.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.0, [("Java", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("PhonePe", "https://www.phonepe.com/careers", "FinTech", "Bengaluru, India", 20.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("Hbase", 4, "Intermediate")]),
    ("CRED", "https://cred.club/careers", "FinTech", "Bengaluru, India", 22.0, "Hard", ["CSE", "IT", "ECE"], 8.0, [("Go", 4, "Intermediate"), ("Ruby on Rails", 4, "Intermediate"), ("React", 4, "Intermediate")]),
    ("BharatPe", "https://bharatpe.com/careers", "FinTech", "New Delhi, India", 14.0, "Medium", ["CSE", "IT", "ECE"], 7.0, [("Node.js", 4, "Intermediate"), ("React", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Groww", "https://groww.in/careers", "FinTech", "Bengaluru, India", 16.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Zerodha", "https://careers.zerodha.com", "FinTech", "Bengaluru, India", 25.0, "Hard", ["CSE", "IT"], 8.0, [("Go", 5, "Expert"), ("Python", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Upstox", "https://upstox.com/careers", "FinTech", "Mumbai, India", 15.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("CoinDCX", "https://coindcx.com/careers", "FinTech", "Mumbai, India", 16.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Node.js", 4, "Intermediate"), ("Go", 4, "Intermediate"), ("MongoDB", 4, "Intermediate")]),
    ("CoinSwitch", "https://coinswitch.co/careers", "FinTech", "Bengaluru, India", 15.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Node.js", 4, "Intermediate"), ("React Native", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Pine Labs", "https://www.pinelabs.com/careers", "FinTech", "Noida, India", 12.0, "Easy", ["CSE", "IT", "ECE"], 7.0, [("Java", 4, "Intermediate"), ("C#", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Billdesk", "https://www.billdesk.com/careers", "FinTech", "Mumbai, India", 10.0, "Easy", ["CSE", "IT", "ECE"], 7.0, [("Java", 4, "Intermediate"), ("Oracle", 4, "Intermediate"), ("Linux", 4, "Intermediate")]),
    ("Affirm", "https://careers.affirm.com", "FinTech", "San Francisco, CA", 26.0, "Medium", ["CSE", "IT"], 7.5, [("Python", 4, "Intermediate"), ("Kotlin", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Block", "https://block.xyz/careers", "FinTech", "San Francisco, CA", 32.0, "Hard", ["CSE", "IT"], 8.0, [("Java", 4, "Intermediate"), ("Go", 4, "Intermediate"), ("Docker", 4, "Intermediate")]),
    ("Brex", "https://brex.com/careers", "FinTech", "San Francisco, CA", 30.0, "Hard", ["CSE", "IT"], 8.0, [("Elixir", 4, "Intermediate"), ("TypeScript", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Carta", "https://carta.com/careers", "FinTech", "San Francisco, CA", 22.0, "Medium", ["CSE", "IT"], 7.5, [("Python", 4, "Intermediate"), ("React", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Circle", "https://www.circle.com/careers", "FinTech", "Boston, MA", 28.0, "Medium", ["CSE", "IT"], 7.5, [("Go", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Checkout.com", "https://www.checkout.com/careers", "FinTech", "London, UK", 24.0, "Medium", ["CSE", "IT"], 7.5, [("C#", 4, "Intermediate"), ("Angular", 4, "Intermediate"), ("Azure", 4, "Intermediate")]),
    ("Melio", "https://www.meliopayments.com/careers", "FinTech", "New York, NY", 22.0, "Medium", ["CSE", "IT"], 7.5, [("TypeScript", 4, "Intermediate"), ("React", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Mercury", "https://mercury.com/jobs", "FinTech", "San Francisco, CA", 28.0, "Hard", ["CSE", "IT"], 8.0, [("Haskell", 4, "Intermediate"), ("React", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Nium", "https://www.nium.com/careers", "FinTech", "Singapore", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("OfBusiness", "https://ofbusiness.com/careers", "FinTech", "Gurugram, India", 15.0, "Medium", ["CSE", "IT", "ECE"], 7.0, [("Python", 4, "Intermediate"), ("Django", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("OneCard", "https://getonecard.app/careers", "FinTech", "Pune, India", 14.0, "Medium", ["CSE", "IT", "ECE"], 7.0, [("Swift", 4, "Intermediate"), ("Kotlin", 4, "Intermediate"), ("Node.js", 4, "Intermediate")]),
    ("Navi", "https://navi.com/careers", "FinTech", "Bengaluru, India", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("React Native", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Slice", "https://sliceit.com/careers", "FinTech", "Bengaluru, India", 15.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Python", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Jupiter", "https://jupiter.money/careers", "FinTech", "Bengaluru, India", 16.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Kotlin", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Fi Money", "https://fi.money/careers", "FinTech", "Bengaluru, India", 16.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Spring", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),

    # 3. E-Commerce & Retail (35 companies)
    ("Walmart", "https://careers.walmart.com", "E-Commerce & Retail", "Bentonville, AR", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Spring Boot", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Target", "https://corporate.target.com/careers", "E-Commerce & Retail", "Minneapolis, MN", 15.0, "Medium", ["CSE", "IT", "ECE"], 7.0, [("Java", 4, "Intermediate"), ("Kotlin", 4, "Intermediate"), ("Docker", 4, "Intermediate")]),
    ("Costco", "https://www.costco.com/jobs.html", "E-Commerce & Retail", "Issaquah, WA", 14.0, "Easy", ["CSE", "IT", "ECE"], 7.0, [("C#", 4, "Intermediate"), ("SQL Server", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("eBay", "https://careers.ebayinc.com", "E-Commerce & Retail", "San Jose, CA", 22.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("Oracle", 4, "Intermediate")]),
    ("Etsy", "https://careers.etsy.com", "E-Commerce & Retail", "Brooklyn, NY", 25.0, "Medium", ["CSE", "IT"], 7.5, [("PHP", 4, "Intermediate"), ("JavaScript", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Shopify", "https://www.shopify.com/careers", "E-Commerce & Retail", "Ottawa, Canada", 28.0, "Hard", ["CSE", "IT"], 8.0, [("Ruby on Rails", 5, "Expert"), ("React", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Swiggy", "https://careers.swiggy.com", "E-Commerce & Delivery", "Bengaluru, India", 18.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("Go", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("Redis", 4, "Intermediate")]),
    ("Zomato", "https://www.zomato.com/careers", "E-Commerce & Delivery", "Gurugram, India", 18.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("PHP", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Flipkart", "https://careers.flipkart.com", "E-Commerce & Retail", "Bengaluru, India", 18.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Myntra", "https://careers.myntra.com", "E-Commerce & Retail", "Bengaluru, India", 16.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Node.js", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MongoDB", 4, "Intermediate")]),
    ("Nykaa", "https://www.nykaa.com/careers", "E-Commerce & Retail", "Mumbai, India", 14.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("React", 4, "Intermediate"), ("PHP", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Ajio", "https://www.ajio.com/careers", "E-Commerce & Retail", "Bengaluru, India", 12.0, "Easy", ["CSE", "IT", "ECE"], 7.0, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Meesho", "https://careers.meesho.com", "E-Commerce & Retail", "Bengaluru, India", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Blinkit", "https://blinkit.com/careers", "E-Commerce & Delivery", "Gurugram, India", 16.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Node.js", 4, "Intermediate"), ("React Native", 4, "Intermediate"), ("MongoDB", 4, "Intermediate")]),
    ("Zepto", "https://www.zeptonow.com/careers", "E-Commerce & Delivery", "Mumbai, India", 16.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Node.js", 4, "Intermediate"), ("React Native", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("BigBasket", "https://www.bigbasket.com/careers", "E-Commerce & Retail", "Bengaluru, India", 12.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 7.0, [("Python", 4, "Intermediate"), ("Django", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Reliance Retail", "https://relianceretail.com/careers", "E-Commerce & Retail", "Mumbai, India", 10.0, "Easy", ["CSE", "IT", "ECE", "MECH"], 7.0, [("Java", 4, "Intermediate"), ("Spring", 4, "Intermediate"), ("Oracle", 4, "Intermediate")]),
    ("Tata CLiQ", "https://www.tatacliq.com/careers", "E-Commerce & Retail", "Mumbai, India", 11.0, "Easy", ["CSE", "IT", "ECE"], 7.0, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("JioMart", "https://www.jiomart.com/careers", "E-Commerce & Retail", "Mumbai, India", 11.0, "Easy", ["CSE", "IT", "ECE"], 7.0, [("Node.js", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("ASOS", "https://www.asos.com/careers", "E-Commerce & Retail", "London, UK", 18.0, "Medium", ["CSE", "IT"], 7.5, [("C#", 4, "Intermediate"), ("React", 4, "Intermediate"), ("Azure", 4, "Intermediate")]),
    ("Zalando", "https://corporate.zalando.com/en/careers", "E-Commerce & Retail", "Berlin, Germany", 22.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Wayfair", "https://www.wayfair.com/careers", "E-Commerce & Retail", "Boston, MA", 20.0, "Medium", ["CSE", "IT"], 7.5, [("PHP", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("MercadoLibre", "https://jobs.mercadolibre.com", "E-Commerce & Retail", "Buenos Aires, Argentina", 22.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("Go", 4, "Intermediate"), ("Redis", 4, "Intermediate")]),
    ("Rakuten", "https://global.rakuten.com/corp/careers", "E-Commerce & Retail", "Tokyo, Japan", 16.0, "Medium", ["CSE", "IT", "ECE"], 7.0, [("Java", 4, "Intermediate"), ("Ruby", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Coupang", "https://www.coupang.jobs", "E-Commerce & Retail", "Seoul, South Korea", 26.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("AWS", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("AliExpress", "https://careers.alibaba.com", "E-Commerce & Retail", "Hangzhou, China", 22.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("C++", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Instacart", "https://instacart.careers", "E-Commerce & Delivery", "San Francisco, CA", 28.0, "Medium", ["CSE", "IT"], 7.5, [("Ruby on Rails", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("DoorDash", "https://careers.doordash.com", "E-Commerce & Delivery", "San Francisco, CA", 32.0, "Hard", ["CSE", "IT"], 8.0, [("Kotlin", 4, "Intermediate"), ("Go", 4, "Intermediate"), ("Redis", 4, "Intermediate")]),
    ("Grubhub", "https://careers.grubhub.com", "E-Commerce & Delivery", "Chicago, IL", 20.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Delivery Hero", "https://careers.deliveryhero.com", "E-Commerce & Delivery", "Berlin, Germany", 24.0, "Medium", ["CSE", "IT"], 7.5, [("Python", 4, "Intermediate"), ("TypeScript", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Deliveroo", "https://deliveroo.co.uk/careers", "E-Commerce & Delivery", "London, UK", 22.0, "Medium", ["CSE", "IT"], 7.5, [("Ruby", 4, "Intermediate"), ("Go", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Swiggy Instamart", "https://careers.swiggy.com", "E-Commerce & Delivery", "Bengaluru, India", 16.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Go", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("Redis", 4, "Intermediate")]),
    ("Dunzo", "https://www.dunzo.com/careers", "E-Commerce & Delivery", "Bengaluru, India", 10.0, "Easy", ["CSE", "IT", "ECE"], 7.0, [("Node.js", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MongoDB", 4, "Intermediate")]),
    ("Bigbasket Daily", "https://www.bigbasket.com/careers", "E-Commerce & Retail", "Bengaluru, India", 11.0, "Easy", ["CSE", "IT", "ECE"], 7.0, [("Python", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("DealShare", "https://www.dealshare.in/careers", "E-Commerce & Retail", "Jaipur, India", 12.0, "Easy", ["CSE", "IT", "ECE"], 7.0, [("Node.js", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),

    # 4. SaaS & Software (45 companies)
    ("HubSpot", "https://careers.hubspot.com", "SaaS & CRM", "Boston, MA", 24.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Zendesk", "https://www.zendesk.com/careers", "SaaS & Cloud", "San Francisco, CA", 20.0, "Medium", ["CSE", "IT"], 7.5, [("Ruby", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Atlassian", "https://www.atlassian.com/careers", "SaaS & Cloud", "Sydney, Australia", 25.0, "Hard", ["CSE", "IT", "ECE"], 8.0, [("Java", 4, "Intermediate"), ("React", 5, "Expert"), ("AWS", 4, "Intermediate")]),
    ("Notion", "https://www.notion.so/careers", "SaaS & Cloud", "San Francisco, CA", 32.0, "Hard", ["CSE", "IT"], 8.0, [("TypeScript", 5, "Expert"), ("Node.js", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Asana", "https://asana.com/jobs", "SaaS & Cloud", "San Francisco, CA", 26.0, "Medium", ["CSE", "IT"], 7.5, [("TypeScript", 4, "Intermediate"), ("React", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Monday.com", "https://monday.com/jobs", "SaaS & Cloud", "Tel Aviv, Israel", 22.0, "Medium", ["CSE", "IT"], 7.5, [("React", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("ClickUp", "https://clickup.com/careers", "SaaS & Cloud", "San Diego, CA", 24.0, "Medium", ["CSE", "IT"], 7.5, [("TypeScript", 4, "Intermediate"), ("Angular", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Smartsheet", "https://www.smartsheet.com/careers", "SaaS & Cloud", "Bellevue, WA", 20.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("AWS", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Airtable", "https://www.airtable.com/careers", "SaaS & Cloud", "San Francisco, CA", 28.0, "Medium", ["CSE", "IT"], 7.5, [("TypeScript", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Snowflake", "https://www.snowflake.com/careers", "SaaS & Cloud", "Bozeman, MT", 34.0, "Hard", ["CSE", "IT"], 8.0, [("C++", 5, "Intermediate"), ("Java", 4, "Intermediate"), ("SQL", 5, "Expert")]),
    ("Databricks", "https://www.databricks.com/careers", "SaaS & Cloud", "San Francisco, CA", 36.0, "Hard", ["CSE", "IT"], 8.5, [("Scala", 5, "Expert"), ("Python", 4, "Intermediate"), ("Spark", 5, "Expert")]),
    ("Elastic", "https://www.elastic.co/careers", "SaaS & Cloud", "Mountain View, CA", 24.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("Elasticsearch", 5, "Expert"), ("Docker", 4, "Intermediate")]),
    ("MongoDB", "https://www.mongodb.com/careers", "SaaS & Cloud", "New York, NY", 26.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 4, "Intermediate"), ("Go", 4, "Intermediate"), ("MongoDB", 5, "Expert")]),
    ("Redis", "https://redis.com/corporate/careers", "SaaS & Cloud", "Mountain View, CA", 25.0, "Medium", ["CSE", "IT"], 7.5, [("C", 5, "Expert"), ("Python", 4, "Intermediate"), ("Redis", 5, "Expert")]),
    ("Neo4j", "https://neo4j.com/careers", "SaaS & Cloud", "San Mateo, CA", 24.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("GraphQL", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Datadog", "https://www.datadoghq.com/careers", "SaaS & Cloud", "New York, NY", 28.0, "Medium", ["CSE", "IT"], 7.5, [("Go", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Docker", 4, "Intermediate")]),
    ("Dynatrace", "https://www.dynatrace.com/company/careers", "SaaS & Cloud", "Waltham, MA", 22.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("C++", 4, "Intermediate"), ("Docker", 4, "Intermediate")]),
    ("New Relic", "https://newrelic.com/about/careers", "SaaS & Cloud", "San Francisco, CA", 24.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("Ruby", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Splunk", "https://www.splunk.com/en_us/careers.html", "SaaS & Cloud", "San Francisco, CA", 24.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Python", 4, "Intermediate"), ("C++", 4, "Intermediate"), ("Linux", 4, "Intermediate")]),
    ("Freshworks", "https://www.freshworks.com/careers", "SaaS & Cloud", "Chennai, India", 15.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Ruby on Rails", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Zoho", "https://www.zoho.com/careers", "SaaS & Cloud", "Chennai, India", 8.0, "Easy", ["CSE", "IT", "ECE", "EEE", "MECH"], 6.5, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Postman", "https://www.postman.com/careers", "SaaS & Cloud", "Bengaluru, India", 20.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("Node.js", 4, "Intermediate"), ("React", 4, "Intermediate"), ("REST APIs", 5, "Expert")]),
    ("BrowserStack", "https://www.browserstack.com/careers", "SaaS & Cloud", "Mumbai, India", 16.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Ruby", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Hasura", "https://hasura.io/careers", "SaaS & Cloud", "Bengaluru, India", 22.0, "Hard", ["CSE", "IT"], 8.0, [("Haskell", 4, "Intermediate"), ("GraphQL", 5, "Expert"), ("PostgreSQL", 4, "Intermediate")]),
    ("Chargebee", "https://www.chargebee.com/careers", "SaaS & Cloud", "Chennai, India", 14.0, "Medium", ["CSE", "IT", "ECE"], 7.0, [("Java", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Okta", "https://www.okta.com/careers", "SaaS & Cloud", "San Francisco, CA", 26.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("REST APIs", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Auth0", "https://auth0.com/careers", "SaaS & Cloud", "Bellevue, WA", 26.0, "Medium", ["CSE", "IT"], 7.5, [("Node.js", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MongoDB", 4, "Intermediate")]),
    ("PagerDuty", "https://www.pagerduty.com/careers", "SaaS & Cloud", "San Francisco, CA", 24.0, "Medium", ["CSE", "IT"], 7.5, [("Ruby", 4, "Intermediate"), ("Elixir", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Twilio", "https://www.twilio.com/careers", "SaaS & Cloud", "San Francisco, CA", 26.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("REST APIs", 5, "Expert")]),
    ("SendGrid", "https://www.twilio.com/careers", "SaaS & Cloud", "Denver, CO", 24.0, "Medium", ["CSE", "IT"], 7.5, [("Go", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Mailchimp", "https://mailchimp.com/jobs", "SaaS & Cloud", "Atlanta, GA", 22.0, "Medium", ["CSE", "IT"], 7.5, [("PHP", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Hubspot Ireland", "https://careers.hubspot.com", "SaaS & Cloud", "Dublin, Ireland", 24.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Intercom", "https://www.intercom.com/careers", "SaaS & Cloud", "Dublin, Ireland", 24.0, "Medium", ["CSE", "IT"], 7.5, [("Ruby on Rails", 4, "Intermediate"), ("React", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Canva", "https://www.canva.com/careers", "SaaS & Cloud", "Sydney, Australia", 25.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("TypeScript", 4, "Intermediate"), ("React", 4, "Intermediate")]),
    ("G2", "https://www.g2.com/careers", "SaaS & Cloud", "Chicago, IL", 16.0, "Medium", ["CSE", "IT"], 7.0, [("Ruby on Rails", 4, "Intermediate"), ("React", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Clari", "https://www.clari.com/careers", "SaaS & Cloud", "Sunnyvale, CA", 22.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Gong", "https://www.gong.io/careers", "SaaS & Cloud", "Tel Aviv, Israel", 26.0, "Medium", ["CSE", "IT"], 7.5, [("Python", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("ServiceNow", "https://www.servicenow.com/careers", "SaaS & Cloud", "Santa Clara, CA", 22.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("JavaScript", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Workday", "https://www.workday.com/careers", "SaaS & Cloud", "Pleasanton, CA", 20.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("Scala", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Sprinklr", "https://www.sprinklr.com/careers", "SaaS & Cloud", "New York, NY", 22.0, "Hard", ["CSE", "IT", "ECE"], 8.0, [("Java", 4, "Intermediate"), ("MongoDB", 4, "Intermediate"), ("Redis", 4, "Intermediate")]),
    ("HighRadius", "https://www.highradius.com/careers", "SaaS & Cloud", "Houston, TX", 10.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 7.0, [("Java", 4, "Intermediate"), ("MySQL", 4, "Intermediate"), ("Spring", 4, "Intermediate")]),
    ("Webflow", "https://webflow.com/careers", "SaaS & Cloud", "San Francisco, CA", 26.0, "Medium", ["CSE", "IT"], 7.5, [("TypeScript", 4, "Intermediate"), ("React", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Zapier", "https://zapier.com/jobs", "SaaS & Cloud", "San Francisco, CA", 24.0, "Medium", ["CSE", "IT"], 7.5, [("Python", 4, "Intermediate"), ("React", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Buffer", "https://buffer.com/journey", "SaaS & Cloud", "San Francisco, CA", 20.0, "Medium", ["CSE", "IT"], 7.5, [("Node.js", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MongoDB", 4, "Intermediate")]),
    ("Hootsuite", "https://www.hootsuite.com/about/careers", "SaaS & Cloud", "Vancouver, Canada", 18.0, "Medium", ["CSE", "IT"], 7.0, [("PHP", 4, "Intermediate"), ("Scala", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),

    # 5. IT Consulting & System Integrators (35 companies)
    ("Accenture", "https://www.accenture.com/careers", "IT Consulting", "Dublin, Ireland", 12.0, "Medium", ["CSE", "IT", "ECE", "EEE", "MECH"], 6.5, [("Java", 3, "Intermediate"), ("SQL", 3, "Intermediate"), ("Git", 3, "Intermediate")]),
    ("TCS", "https://www.tcs.com/careers", "IT Services", "Mumbai, India", 7.0, "Easy", ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"], 6.0, [("Python", 3, "Beginner"), ("Java", 3, "Beginner"), ("SQL", 3, "Beginner")]),
    ("Infosys", "https://www.infosys.com/careers", "IT Services", "Bengaluru, India", 6.8, "Easy", ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"], 6.0, [("Python", 3, "Beginner"), ("Java", 3, "Beginner"), ("SQL", 3, "Beginner")]),
    ("Wipro", "https://careers.wipro.com", "IT Services", "Bengaluru, India", 6.5, "Easy", ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"], 6.0, [("Python", 3, "Beginner"), ("Java", 3, "Beginner"), ("SQL", 3, "Beginner")]),
    ("Cognizant", "https://careers.cognizant.com", "IT Services", "Teaneck, NJ", 7.5, "Easy", ["CSE", "IT", "ECE", "EEE", "MECH"], 6.0, [("Java", 3, "Beginner"), ("C#", 3, "Beginner"), ("SQL", 3, "Beginner")]),
    ("Capgemini", "https://www.capgemini.com/careers", "IT Services", "Paris, France", 7.5, "Easy", ["CSE", "IT", "ECE", "EEE", "MECH"], 6.0, [("Java", 3, "Beginner"), ("Python", 3, "Beginner"), ("SQL", 3, "Beginner")]),
    ("Deloitte", "https://www2.deloitte.com/careers", "IT Consulting", "London, UK", 12.5, "Medium", ["CSE", "IT", "ECE", "EEE", "MECH"], 7.0, [("Python", 3, "Intermediate"), ("SQL", 4, "Intermediate"), ("Tableau", 4, "Intermediate")]),
    ("PwC", "https://www.pwc.com/careers", "IT Consulting", "London, UK", 11.5, "Medium", ["CSE", "IT", "ECE", "EEE", "MECH"], 7.0, [("SQL", 4, "Intermediate"), ("Excel", 4, "Intermediate"), ("Python", 3, "Beginner")]),
    ("EY", "https://www.ey.com/careers", "IT Consulting", "London, UK", 11.5, "Medium", ["CSE", "IT", "ECE", "EEE", "MECH"], 7.0, [("SQL", 4, "Intermediate"), ("Power BI", 4, "Intermediate"), ("Excel", 4, "Intermediate")]),
    ("KPMG", "https://kpmg.com/careers", "IT Consulting", "Amstelveen, Netherlands", 11.5, "Medium", ["CSE", "IT", "ECE", "EEE", "MECH"], 7.0, [("SQL", 4, "Intermediate"), ("Power BI", 4, "Intermediate"), ("Excel", 4, "Intermediate")]),
    ("DXC Technology", "https://dxc.com/careers", "IT Services", "Ashburn, VA", 6.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.0, [("Java", 3, "Beginner"), ("SQL", 3, "Beginner"), ("Linux", 3, "Beginner")]),
    ("LTIMindtree", "https://www.ltimindtree.com/careers", "IT Services", "Mumbai, India", 8.0, "Easy", ["CSE", "IT", "ECE", "EEE", "MECH"], 6.5, [("Java", 3, "Intermediate"), ("Python", 3, "Intermediate"), ("SQL", 3, "Intermediate")]),
    ("Tech Mahindra", "https://www.techmahindra.com/careers", "IT Services", "Pune, India", 6.5, "Easy", ["CSE", "IT", "ECE", "EEE", "MECH"], 6.0, [("Python", 3, "Beginner"), ("Java", 3, "Beginner"), ("SQL", 3, "Beginner")]),
    ("HCLTech", "https://www.hcltech.com/careers", "IT Services", "Noida, India", 7.0, "Easy", ["CSE", "IT", "ECE", "EEE", "MECH"], 6.0, [("Java", 3, "Beginner"), ("C++", 3, "Beginner"), ("SQL", 3, "Beginner")]),
    ("Hexaware", "https://hexaware.com/careers", "IT Services", "Mumbai, India", 6.5, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.0, [("Java", 3, "Beginner"), ("Python", 3, "Beginner"), ("SQL", 3, "Beginner")]),
    ("Virtusa", "https://www.virtusa.com/careers", "IT Services", "Southborough, MA", 6.8, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.0, [("Java", 3, "Beginner"), ("React", 3, "Beginner"), ("SQL", 3, "Beginner")]),
    ("EPAM", "https://www.epam.com/careers", "IT Consulting", "Newtown, PA", 14.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("JavaScript", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Globant", "https://www.globant.com/careers", "IT Consulting", "Luxembourg", 12.0, "Medium", ["CSE", "IT", "ECE"], 7.0, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Endava", "https://www.endava.com/careers", "IT Consulting", "London, UK", 12.0, "Medium", ["CSE", "IT", "ECE"], 7.0, [("Java", 4, "Intermediate"), ("C#", 4, "Intermediate"), ("SQL", 3, "Intermediate")]),
    ("Thoughtworks", "https://www.thoughtworks.com/careers", "IT Consulting", "Chicago, IL", 16.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("Docker", 4, "Intermediate")]),
    ("Persistent Systems", "https://www.persistent.com/careers", "IT Services", "Pune, India", 9.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.5, [("Java", 3, "Intermediate"), ("Python", 3, "Intermediate"), ("SQL", 3, "Intermediate")]),
    ("Zensar", "https://www.zensar.com/careers", "IT Services", "Pune, India", 6.5, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.0, [("Java", 3, "Beginner"), ("SQL", 3, "Beginner"), ("HTML", 3, "Beginner")]),
    ("Coforge", "https://www.coforge.com/careers", "IT Services", "Noida, India", 8.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.5, [("Java", 3, "Intermediate"), ("SQL", 3, "Intermediate"), ("Spring", 3, "Intermediate")]),
    ("Sonata Software", "https://www.sonata-software.com/careers", "IT Services", "Bengaluru, India", 7.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.0, [("Java", 3, "Beginner"), ("C#", 3, "Beginner"), ("SQL", 3, "Beginner")]),
    ("Mphasis", "https://www.mphasis.com/careers", "IT Services", "Bengaluru, India", 7.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.0, [("Java", 3, "Beginner"), ("SQL", 3, "Beginner"), ("Linux", 3, "Beginner")]),
    ("Accenture Federal", "https://www.accenture.com/careers", "IT Consulting", "Arlington, VA", 12.0, "Medium", ["CSE", "IT", "ECE"], 7.0, [("Java", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Linux", 4, "Intermediate")]),
    ("Deloitte India", "https://www2.deloitte.com/careers", "IT Consulting", "Hyderabad, India", 8.5, "Medium", ["CSE", "IT", "ECE", "EEE"], 6.5, [("Java", 3, "Intermediate"), ("SQL", 3, "Intermediate"), ("Excel", 3, "Intermediate")]),
    ("PwC India", "https://www.pwc.com/careers", "IT Consulting", "Mumbai, India", 8.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 6.5, [("SQL", 3, "Intermediate"), ("Excel", 3, "Intermediate"), ("Tableau", 3, "Intermediate")]),
    ("EY India", "https://www.ey.com/careers", "IT Consulting", "Bengaluru, India", 8.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 6.5, [("SQL", 3, "Intermediate"), ("Power BI", 3, "Intermediate"), ("Excel", 3, "Intermediate")]),
    ("KPMG India", "https://kpmg.com/careers", "IT Consulting", "Mumbai, India", 8.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 6.5, [("SQL", 3, "Intermediate"), ("Power BI", 3, "Intermediate"), ("Excel", 3, "Intermediate")]),
    ("Accenture India", "https://www.accenture.com/careers", "IT Services", "Bengaluru, India", 7.5, "Easy", ["CSE", "IT", "ECE", "EEE", "MECH"], 6.0, [("Java", 3, "Beginner"), ("SQL", 3, "Beginner"), ("Git", 3, "Beginner")]),
    ("Birlasoft", "https://www.birlasoft.com/careers", "IT Services", "Noida, India", 6.5, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.0, [("Java", 3, "Beginner"), ("SQL", 3, "Beginner"), ("Spring", 3, "Beginner")]),
    ("KPIT Technologies", "https://www.kpit.com/careers", "IT Services", "Pune, India", 7.0, "Easy", ["CSE", "IT", "ECE", "EEE", "MECH"], 6.0, [("C++", 3, "Beginner"), ("Python", 3, "Beginner"), ("Embedded C", 4, "Intermediate")]),
    ("Cyient", "https://www.cyient.com/careers", "IT Services", "Hyderabad, India", 6.5, "Easy", ["CSE", "IT", "ECE", "MECH"], 6.0, [("C++", 3, "Beginner"), ("SQL", 3, "Beginner"), ("AutoCAD", 4, "Intermediate")]),
    ("UST Global", "https://ust.com/careers", "IT Services", "Aliso Viejo, CA", 7.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.0, [("Java", 3, "Beginner"), ("React", 3, "Beginner"), ("SQL", 3, "Beginner")]),

    # 6. Finance & Banking (30 companies)
    ("Goldman Sachs", "https://careers.goldmansachs.com", "Investment Banking", "New York, NY", 25.0, "Hard", ["CSE", "IT", "ECE"], 8.0, [("Java", 5, "Expert"), ("C++", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("JPMorgan Chase", "https://careers.jpmorgan.com", "Investment Banking", "New York, NY", 22.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Morgan Stanley", "https://www.morganstanley.com/careers", "Investment Banking", "New York, NY", 20.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("C++", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Citigroup", "https://careers.citigroup.com", "Investment Banking", "New York, NY", 18.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("Java", 4, "Intermediate"), ("Spring Boot", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("HSBC", "https://www.hsbc.com/careers", "Commercial Banking", "London, UK", 16.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.0, [("Java", 4, "Intermediate"), ("Spring", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Barclays", "https://search.jobs.barclays", "Commercial Banking", "London, UK", 18.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("Java", 4, "Intermediate"), ("Spring Boot", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Deutsche Bank", "https://careers.db.com", "Investment Banking", "Frankfurt, Germany", 19.5, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("UBS", "https://www.ubs.com/careers", "Investment Banking", "Zurich, Switzerland", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Spring Boot", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Credit Suisse", "https://www.credit-suisse.com/careers", "Investment Banking", "Zurich, Switzerland", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Oracle", 4, "Intermediate"), ("SQL", 3, "Intermediate")]),
    ("Bank of America", "https://careers.bankofamerica.com", "Commercial Banking", "Charlotte, NC", 18.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("Java", 4, "Intermediate"), ("Spring", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Wells Fargo", "https://www.wellsfargojobs.com", "Commercial Banking", "San Francisco, CA", 18.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("Java", 4, "Intermediate"), ("C#", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("American Express", "https://careers.americanexpress.com", "Commercial Banking", "New York, NY", 22.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Visa", "https://careers.visa.com", "Commercial Banking", "Foster City, CA", 26.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("Java", 4, "Intermediate"), ("REST APIs", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Mastercard", "https://careers.mastercard.com", "Commercial Banking", "Purchase, NY", 24.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("Java", 4, "Intermediate"), ("REST APIs", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Capital One", "https://www.capitalonecareers.com", "Commercial Banking", "McLean, VA", 28.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Discover", "https://jobs.discover.com", "Commercial Banking", "Riverwoods, IL", 20.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Spring Boot", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Fidelity", "https://jobs.fidelity.com", "Commercial Banking", "Boston, MA", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("AWS", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Vanguard", "https://www.vanguardjobs.com", "Commercial Banking", "Malvern, PA", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("AWS", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("BlackRock", "https://careers.blackrock.com", "Commercial Banking", "New York, NY", 22.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Charles Schwab", "https://www.aboutschwab.com/careers", "Commercial Banking", "Westlake, TX", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("C#", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Angular", 4, "Intermediate")]),
    ("HDFC Bank", "https://careers.hdfcbank.com", "Commercial Banking", "Mumbai, India", 12.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 7.0, [("Java", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Oracle", 4, "Intermediate")]),
    ("ICICI Bank", "https://www.icicicareers.com", "Commercial Banking", "Mumbai, India", 11.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 7.0, [("Java", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Oracle", 4, "Intermediate")]),
    ("Axis Bank", "https://www.axisbank.com/careers", "Commercial Banking", "Mumbai, India", 11.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 7.0, [("Java", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Oracle", 4, "Intermediate")]),
    ("Kotak Mahindra", "https://careers.kotak.com", "Commercial Banking", "Mumbai, India", 11.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 7.0, [("Java", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Oracle", 4, "Intermediate")]),
    ("State Bank of India", "https://sbi.co.in/careers", "Commercial Banking", "Mumbai, India", 9.0, "Hard", ["CSE", "IT", "ECE", "EEE", "MECH"], 6.0, [("SQL", 3, "Beginner"), ("Excel", 4, "Intermediate"), ("Aptitude", 5, "Expert")]),
    ("JPMorgan India", "https://careers.jpmorgan.com", "Investment Banking", "Mumbai, India", 16.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Goldman Sachs India", "https://careers.goldmansachs.com", "Investment Banking", "Bengaluru, India", 22.0, "Hard", ["CSE", "IT", "ECE"], 8.0, [("Java", 4, "Intermediate"), ("C++", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Morgan Stanley India", "https://www.morganstanley.com/careers", "Investment Banking", "Mumbai, India", 16.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("C++", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Citigroup India", "https://careers.citigroup.com", "Investment Banking", "Mumbai, India", 14.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("Java", 4, "Intermediate"), ("Spring", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Barclays India", "https://search.jobs.barclays", "Commercial Banking", "Pune, India", 14.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("Java", 4, "Intermediate"), ("Spring Boot", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),

    # 7. Automotive, Aerospace & Hardware Manufacturing (30 companies)
    ("SpaceX", "https://www.spacex.com/careers", "Technology", "Hawthorne, CA", 28.0, "Hard", ["CSE", "IT", "ECE", "MECH", "EEE"], 8.0, [("C++", 5, "Expert"), ("Python", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Boeing", "https://jobs.boeing.com", "Technology", "Chicago, IL", 16.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("Ada", 4, "Intermediate")]),
    ("Lockheed Martin", "https://www.lockheedmartinjobs.com", "Technology", "Bethesda, MD", 15.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Java", 4, "Intermediate")]),
    ("Northrop Grumman", "https://careers.northropgrumman.com", "Technology", "Falls Church, VA", 15.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("C#", 4, "Intermediate")]),
    ("General Dynamics", "https://www.gd.com/careers", "Technology", "Reston, VA", 14.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Windows", 4, "Intermediate")]),
    ("Raytheon", "https://careers.rtx.com", "Technology", "Arlington, VA", 15.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Matlab", 4, "Intermediate")]),
    ("Ford", "https://careers.ford.com", "Automotive", "Dearborn, MI", 14.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.0, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("GM", "https://search-careers.gm.com", "Automotive", "Detroit, MI", 14.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.0, [("C++", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Toyota", "https://www.toyota.com/usa/careers", "Automotive", "Toyota, Japan", 15.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.0, [("C++", 4, "Intermediate"), ("C", 4, "Intermediate"), ("Python", 4, "Intermediate")]),
    ("Honda", "https://www.honda.com/careers", "Automotive", "Tokyo, Japan", 14.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.0, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Nissan", "https://www.nissan_careers.com", "Automotive", "Yokohama, Japan", 13.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.0, [("C++", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("Linux", 4, "Intermediate")]),
    ("Hyundai", "https://www.hyundai.com/worldwide/en/company/careers", "Automotive", "Seoul, South Korea", 14.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.0, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Matlab", 4, "Intermediate")]),
    ("BMW", "https://www.bmwgroup.jobs", "Automotive", "Munich, Germany", 18.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Docker", 4, "Intermediate")]),
    ("Mercedes-Benz", "https://group-careers.mercedes-benz.com", "Automotive", "Stuttgart, Germany", 18.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Audi", "https://www.audi.com/careers", "Automotive", "Ingolstadt, Germany", 17.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Docker", 4, "Intermediate")]),
    ("Porsche", "https://newsroom.porsche.com/en/company/careers.html", "Automotive", "Stuttgart, Germany", 20.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Volkswagen", "https://www.volkswagen-group-careers.com", "Automotive", "Wolfsburg, Germany", 15.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.0, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Volvo", "https://www.volvogroup.com/en/career.html", "Automotive", "Gothenburg, Sweden", 15.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.0, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Ferrari", "https://www.ferrari.com/en-EN/corporate/careers", "Automotive", "Maranello, Italy", 22.0, "Hard", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.5, [("C++", 5, "Expert"), ("Matlab", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Lamborghini", "https://www.lamborghini.com/en-lock/careers", "Automotive", "Sant'Agata Bolognese, Italy", 20.0, "Medium", ["CSE", "IT", "ECE", "MECH", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Tata Motors", "https://www.tatamotors.com/careers", "Automotive", "Mumbai, India", 8.0, "Easy", ["MECH", "EEE", "ECE", "CSE", "IT"], 6.5, [("AutoCAD", 4, "Intermediate"), ("Matlab", 3, "Beginner"), ("C++", 3, "Beginner")]),
    ("Mahindra & Mahindra", "https://www.mahindra.com/careers", "Automotive", "Mumbai, India", 8.0, "Easy", ["MECH", "EEE", "ECE", "CSE", "IT"], 6.5, [("AutoCAD", 4, "Intermediate"), ("Ansys", 4, "Intermediate"), ("Python", 3, "Beginner")]),
    ("Maruti Suzuki", "https://www.marutisuzuki.com/corporate/careers", "Automotive", "New Delhi, India", 9.0, "Easy", ["MECH", "EEE", "ECE", "CSE", "IT"], 6.5, [("AutoCAD", 4, "Intermediate"), ("SQL", 3, "Beginner"), ("Excel", 4, "Intermediate")]),
    ("Hero MotoCorp", "https://www.heromotocorp.com/en-in/careers.html", "Automotive", "New Delhi, India", 8.0, "Easy", ["MECH", "EEE", "ECE", "CSE"], 6.5, [("AutoCAD", 4, "Intermediate"), ("Ansys", 3, "Beginner"), ("Excel", 4, "Intermediate")]),
    ("Bajaj Auto", "https://www.bajajauto.com/careers", "Automotive", "Pune, India", 8.5, "Easy", ["MECH", "EEE", "ECE", "CSE"], 6.5, [("AutoCAD", 4, "Intermediate"), ("Excel", 4, "Intermediate"), ("SolidWorks", 4, "Intermediate")]),
    ("NIO", "https://www.nio.com/careers", "Automotive", "Shanghai, China", 22.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Linux", 4, "Intermediate")]),
    ("Rivian", "https://rivian.com/careers", "Automotive", "Irvine, CA", 26.0, "Hard", ["CSE", "IT", "ECE", "EEE"], 7.5, [("C++", 5, "Intermediate"), ("Python", 4, "Intermediate"), ("Docker", 4, "Intermediate")]),
    ("Lucid Motors", "https://www.lucidmotors.com/careers", "Automotive", "Newark, CA", 25.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Bosch India", "https://www.bosch.in/careers", "Engineering", "Bengaluru, India", 7.5, "Easy", ["ECE", "EEE", "CSE", "IT", "MECH"], 6.5, [("Embedded C", 4, "Intermediate"), ("C++", 3, "Beginner"), ("Matlab", 4, "Intermediate")]),
    ("Siemens India", "https://www.siemens.com/in/en/company/jobs.html", "Engineering", "Mumbai, India", 8.0, "Easy", ["EEE", "ECE", "CSE", "IT", "MECH"], 6.5, [("PLC Programming", 4, "Intermediate"), ("SQL", 3, "Beginner"), ("Java", 3, "Beginner")]),

    # 8. Gaming (25 companies)
    ("EA", "https://www.ea.com/careers", "Gaming", "Redwood City, CA", 22.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("C#", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Ubisoft", "https://www.ubisoft.com/en-us/company/careers", "Gaming", "Montreuil, France", 18.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("Python", 4, "Intermediate"), ("Unreal Engine", 4, "Intermediate")]),
    ("Take-Two", "https://www.take2games.com/careers", "Gaming", "New York, NY", 24.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("C#", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Rockstar Games", "https://www.rockstargames.com/careers", "Gaming", "New York, NY", 28.0, "Hard", ["CSE", "IT"], 8.0, [("C++", 5, "Expert"), ("Python", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Valve", "https://www.valvesoftware.com/en/jobs", "Gaming", "Bellevue, WA", 38.0, "Hard", ["CSE", "IT"], 8.5, [("C++", 5, "Expert"), ("Python", 4, "Intermediate"), ("Linux", 4, "Intermediate")]),
    ("Epic Games", "https://www.epicgames.com/careers", "Gaming", "Cary, NC", 30.0, "Hard", ["CSE", "IT"], 8.0, [("C++", 5, "Expert"), ("Unreal Engine", 5, "Expert"), ("Python", 4, "Intermediate")]),
    ("Nintendo", "https://careers.nintendo.com", "Gaming", "Kyoto, Japan", 20.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("C++", 5, "Expert"), ("C", 4, "Intermediate"), ("Assembly", 4, "Intermediate")]),
    ("Sega", "https://www.sega.co.jp/english/career", "Gaming", "Tokyo, Japan", 16.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("C#", 4, "Intermediate"), ("Unity", 4, "Intermediate")]),
    ("Capcom", "https://www.capcom.co.jp/recruit/index_e.html", "Gaming", "Osaka, Japan", 16.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("C#", 4, "Intermediate"), ("Python", 4, "Intermediate")]),
    ("Square Enix", "https://www.hd.square-enix.com/eng/recruit", "Gaming", "Tokyo, Japan", 18.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("Unreal Engine", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Bandai Namco", "https://www.bandainamco.co.jp/en/recruit/index.html", "Gaming", "Tokyo, Japan", 15.0, "Easy", ["CSE", "IT", "ECE"], 7.0, [("C++", 4, "Intermediate"), ("C#", 4, "Intermediate"), ("Unity", 4, "Intermediate")]),
    ("Riot Games", "https://www.riotgames.com/en/work-with-us", "Gaming", "Los Angeles, CA", 32.0, "Hard", ["CSE", "IT"], 8.0, [("C++", 5, "Expert"), ("Java", 4, "Intermediate"), ("Python", 4, "Intermediate")]),
    ("CD Projekt Red", "https://en.cdprojektred.com/jobs", "Gaming", "Warsaw, Poland", 20.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("Python", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("FromSoftware", "https://www.fromsoftware.jp/ww/recruit.html", "Gaming", "Tokyo, Japan", 22.0, "Hard", ["CSE", "IT"], 8.0, [("C++", 5, "Expert"), ("C#", 4, "Intermediate"), ("Unity", 4, "Intermediate")]),
    ("Bungie", "https://careers.bungie.com", "Gaming", "Bellevue, WA", 26.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("C#", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Unity Technologies", "https://careers.unity.com", "Gaming", "San Francisco, CA", 26.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("C#", 5, "Expert"), ("Unity", 5, "Expert")]),
    ("Roblox", "https://corp.roblox.com/careers", "Gaming", "San Mateo, CA", 36.0, "Hard", ["CSE", "IT"], 8.5, [("C++", 5, "Expert"), ("Go", 4, "Intermediate"), ("Luau", 5, "Expert")]),
    ("Activision", "https://careers.activision.com", "Gaming", "Santa Monica, CA", 26.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("C#", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Blizzard", "https://careers.blizzard.com", "Gaming", "Irvine, CA", 26.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("Java", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Bethesda", "https://jobs.zenimax.com", "Gaming", "Rockville, MD", 24.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("C#", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Bioware", "https://www.bioware.com/careers", "Gaming", "Edmonton, Canada", 22.0, "Medium", ["CSE", "IT"], 7.5, [("C++", 5, "Expert"), ("Python", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Zynga", "https://www.zynga.com/careers", "Gaming", "San Francisco, CA", 18.0, "Easy", ["CSE", "IT", "ECE"], 7.0, [("Java", 4, "Intermediate"), ("JavaScript", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Supercell", "https://supercell.com/en/careers", "Gaming", "Helsinki, Finland", 30.0, "Hard", ["CSE", "IT"], 8.0, [("C++", 5, "Expert"), ("Objective-C", 4, "Intermediate"), ("Java", 4, "Intermediate")]),
    ("King", "https://careers.king.com", "Gaming", "London, UK", 22.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("C++", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Playrix", "https://playrix.com/careers", "Gaming", "Dublin, Ireland", 16.0, "Easy", ["CSE", "IT", "ECE"], 7.0, [("C++", 4, "Intermediate"), ("C#", 4, "Intermediate"), ("Unity", 4, "Intermediate")]),

    # 9. EdTech, Telecom, Healthcare & Others (20 companies)
    ("Coursera", "https://about.coursera.org/careers", "EdTech", "Mountain View, CA", 22.0, "Medium", ["CSE", "IT"], 7.5, [("Scala", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Udacity", "https://www.udacity.com/careers", "EdTech", "Mountain View, CA", 20.0, "Medium", ["CSE", "IT"], 7.5, [("Python", 4, "Intermediate"), ("React", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Udemy", "https://about.udemy.com/careers", "EdTech", "San Francisco, CA", 20.0, "Medium", ["CSE", "IT"], 7.5, [("Python", 4, "Intermediate"), ("Django", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("edX", "https://www.edx.org/careers", "EdTech", "Lanham, MD", 18.0, "Medium", ["CSE", "IT"], 7.5, [("Python", 4, "Intermediate"), ("Django", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Duolingo", "https://careers.duolingo.com", "EdTech", "Pittsburgh, PA", 28.0, "Hard", ["CSE", "IT"], 8.0, [("Python", 4, "Intermediate"), ("Kotlin", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("BYJU'S", "https://byjus.com/careers", "EdTech", "Bengaluru, India", 10.0, "Easy", ["CSE", "IT", "ECE", "EEE", "MECH"], 6.0, [("Java", 3, "Beginner"), ("MySQL", 3, "Beginner"), ("Excel", 4, "Intermediate")]),
    ("Unacademy", "https://unacademy.com/careers", "EdTech", "Bengaluru, India", 12.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.5, [("Node.js", 3, "Intermediate"), ("React", 4, "Intermediate"), ("MongoDB", 3, "Beginner")]),
    ("Simplilearn", "https://www.simplilearn.com/careers", "EdTech", "Bengaluru, India", 8.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.0, [("Java", 3, "Beginner"), ("React", 3, "Beginner"), ("MySQL", 3, "Beginner")]),
    ("PhysicsWallah", "https://www.pw.live/careers", "EdTech", "Noida, India", 10.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.5, [("Node.js", 3, "Intermediate"), ("React", 4, "Intermediate"), ("PostgreSQL", 3, "Beginner")]),
    ("Verizon", "https://www.verizon.com/about/careers", "Telecom", "New York, NY", 15.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.0, [("Java", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Linux", 4, "Intermediate")]),
    ("AT&T", "https://www.att.jobs", "Telecom", "Dallas, TX", 14.5, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.0, [("Java", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Nginx", 4, "Intermediate")]),
    ("T-Mobile", "https://www.t-mobile.com/careers", "Telecom", "Bellevue, WA", 14.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.0, [("C#", 4, "Intermediate"), ("SQL Server", 4, "Intermediate"), ("Azure", 4, "Intermediate")]),
    ("Vodafone", "https://careers.vodafone.com", "Telecom", "London, UK", 14.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.0, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Jio", "https://careers.jio.com", "Telecom", "Mumbai, India", 10.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.5, [("Java", 3, "Intermediate"), ("Python", 3, "Intermediate"), ("MySQL", 3, "Beginner")]),
    ("Airtel", "https://www.airtel.in/careers", "Telecom", "New Delhi, India", 12.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 7.0, [("Java", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("MySQL", 4, "Intermediate")]),
    ("Vi", "https://www.myvi.in/careers", "Telecom", "Mumbai, India", 8.0, "Easy", ["CSE", "IT", "ECE", "EEE"], 6.0, [("Java", 3, "Beginner"), ("SQL", 3, "Beginner"), ("Excel", 4, "Intermediate")]),
    ("Pfizer", "https://careers.pfizer.com", "Healthcare", "New York, NY", 12.0, "Easy", ["CSE", "IT", "ECE", "MECH"], 7.0, [("Python", 3, "Beginner"), ("SQL", 4, "Intermediate"), ("Excel", 4, "Intermediate")]),
    ("Moderna", "https://modernatx.wd1.myworkdayjobs.com/Moderna", "Healthcare", "Cambridge, MA", 14.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Python", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("AWS", 4, "Intermediate")]),
    ("Johnson & Johnson", "https://careers.jnj.com", "Healthcare", "New Brunswick, NJ", 14.0, "Easy", ["CSE", "IT", "ECE", "MECH"], 7.0, [("Java", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Excel", 4, "Intermediate")]),
    ("AstraZeneca", "https://careers.astrazeneca.com", "Healthcare", "Cambridge, UK", 13.0, "Medium", ["CSE", "IT", "ECE"], 7.0, [("Python", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("AWS", 4, "Intermediate")])
]

# Additional 100+ Indian startup / corporate companies to bring the total to 315
ADDITIONAL_COMPANIES = [
    ("Netflix India", "https://jobs.netflix.com", "Technology", "Mumbai, India", 28.0, "Hard", ["CSE", "IT"], 8.0, [("Java", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Kafka", 4, "Intermediate")]),
    ("Adobe India", "https://www.adobe.com/careers", "Technology", "Noida, India", 22.0, "Medium", ["CSE", "IT", "ECE"], 8.0, [("C++", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("JavaScript", 4, "Intermediate")]),
    ("Spotify India", "https://www.lifeatspotify.com", "Technology", "Mumbai, India", 20.0, "Medium", ["CSE", "IT"], 7.5, [("Java", 4, "Intermediate"), ("React", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Salesforce India", "https://careers.salesforce.com", "SaaS & Cloud", "Bengaluru, India", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Salesforce Apex", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Uber India", "https://www.uber.com/careers", "Technology", "Bengaluru, India", 25.0, "Hard", ["CSE", "IT", "ECE"], 8.0, [("Go", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("Redis", 4, "Intermediate")]),
    ("Oracle India", "https://careers.oracle.com", "SaaS & Cloud", "Bengaluru, India", 14.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Linux", 4, "Intermediate")]),
    ("Cisco India", "https://jobs.cisco.com", "Technology", "Bengaluru, India", 15.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("Python", 4, "Intermediate"), ("Nginx", 4, "Intermediate"), ("Docker", 4, "Intermediate")]),
    ("AMD India", "https://careers.amd.com", "Technology", "Bengaluru, India", 16.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("NVIDIA India", "https://www.nvidia.com/careers", "Technology", "Bengaluru, India", 25.0, "Hard", ["CSE", "IT", "ECE", "EEE"], 8.0, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("CUDA", 4, "Intermediate")]),
    ("Qualcomm India", "https://www.qualcomm.com/careers", "Technology", "Bengaluru, India", 15.5, "Medium", ["ECE", "CSE", "EEE"], 7.5, [("C", 4, "Intermediate"), ("C++", 4, "Intermediate"), ("Python", 4, "Intermediate")]),
    ("Intel India", "https://jobs.intel.com", "Technology", "Bengaluru, India", 15.0, "Medium", ["CSE", "IT", "ECE", "EEE"], 7.5, [("C++", 4, "Intermediate"), ("Python", 4, "Intermediate"), ("Git", 4, "Intermediate")]),
    ("Zoom India", "https://careers.zoom.us", "Technology", "Bengaluru, India", 15.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("C++", 4, "Intermediate"), ("Java", 4, "Intermediate"), ("Nginx", 4, "Intermediate")]),
    ("Paypal India", "https://careers.pypl.com", "FinTech", "Bengaluru, India", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("Node.js", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate")]),
    ("Visa India", "https://careers.visa.com", "Commercial Banking", "Bengaluru, India", 20.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("REST APIs", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
    ("Mastercard India", "https://careers.mastercard.com", "Commercial Banking", "Pune, India", 18.0, "Medium", ["CSE", "IT", "ECE"], 7.5, [("Java", 4, "Intermediate"), ("REST APIs", 4, "Intermediate"), ("SQL", 4, "Intermediate")]),
]

# Real Indian startup names to generate the remainder of the 315 list
base_names = [
    "Ola Cabs", "Swiggy Delivery", "Flipkart Wholesale", "InMobi", "Paytm Money", "Pharmeasy", "Pine Labs India",
    "Udaan", "Postman Inc", "Lenskart", "Nykaa Retail", "Dailyhunt", "ShareChat", "Digit Insurance", "Razorpay Software",
    "Swiggy Dineout", "Zomato Gold", "Blinkit Commerce", "Zepto Express", "BigBasket Retail", "Tata Neu", "Cred Club",
    "Groww Investments", "Zerodha Tech", "Navi Insurance", "Slice Cards", "Jupiter Bank", "Fi Money Tech", "OneCard Tech",
    "BharatPe Tech", "Spinny", "Cars24", "Cardekho", "Bikewale", "BookMyShow", "MakeMyTrip", "Yatra", "Cleartrip",
    "RedBus", "Abhibus", "EaseMyTrip", "Urban Company", "Housejoy", "NoBroker", "MagicBricks", "99acres", "Housing.com",
    "Proptiger", "Square Yards", "Anarock", "Oyo Rooms", "Treebo", "FabHotels", "Stayzilla", "Goibibo",
    "Redbus India", "ixigo", "ConfirmTkt", "RailYatri", "Chalo Cabs", "Shuttl", "Rapido", "Bounce",
    "Yulu", "Vogo", "Drivezy", "Zoomcar", "Myles", "Revv", "Ather Energy", "Ola Electric",
    "Revolt Motors", "Tork Motors", "Ultraviolette Automotive", "Pravaig Dynamics", "Euler Motors", "Altigreen",
    "Lohia Auto", "Hero Electric", "Okinawa Autotech", "Ampere Vehicles", "TVS iQube", "Chetak Electric",
    "Bajaj Chetak", "Bounce Infinity", "Simple Energy", "Matter Motor", "Oben Electric", "Hop Electric",
    "Komaki", "Pure EV", "Joy E-Bike", "EeVe India", "Okaya EV", "Odysse EV", "Wardwizard",
    "Geliose Mobility", "Detel EV", "Trouve Motor", "Raptee Energy", "Orxa Energies", "Gravton Motors",
    "Kabira Mobility", "Tunwal E-Bike", "Techo Electra", "Benling India", "Evolet India", "Li-ions Elektrik",
    "Batt:RE", "Gemopai", "Corrit Electric", "Rivo EV", "One Electric", "Kridn", "Svitch Moto",
    "Enigma GT", "Atumobile", "Evric", "Voltron", "Aptitude EV", "Spark EV", "Electron EV",
    "Velo EV", "Sonic EV", "Nimbus EV", "Pioneer EV", "Titan EV", "Atlas EV", "Galaxy EV",
    "Orbit EV", "Comet EV", "Meteor EV", "Aero EV", "Nova EV", "Prime EV", "Zenith EV",
    "Apex EV", "Vector EV", "Summit EV", "Ridge EV", "Peak EV", "Crest EV", "Vale EV",
    "Delta EV", "Gamma EV", "Beta EV", "Alpha EV", "Omega EV", "Sigma EV", "Theta EV"
]

all_seeded_names = set(c[0] for c in COMPANIES_DATA)
all_seeded_names.update(c[0] for c in ADDITIONAL_COMPANIES)

# Build dynamic companies until we have 315 total
index = 0
while len(COMPANIES_DATA) + len(ADDITIONAL_COMPANIES) < 315 and index < len(base_names):
    name = base_names[index]
    index += 1
    if name in all_seeded_names:
        continue
    
    # Direct mappings based on real company categories
    if "Bank" in name or "Money" in name or "Insurance" in name or "Investments" in name or "Fin" in name or "Card" in name or "Pay" in name or "Cred" in name:
        industry = "FinTech"
    elif "Delivery" in name or "Mart" in name or "Wholesale" in name or "Retail" in name or "Express" in name or "Rooms" in name or "Hotels" in name or "Cabs" in name:
        industry = "E-Commerce & Delivery" if "Delivery" in name or "Express" in name or "Cabs" in name else "E-Commerce & Retail"
    elif "Motors" in name or "Electric" in name or "EV" in name or "Automotive" in name or "Engine" in name or "Energy" in name:
        industry = "Automotive"
    else:
        industry = "SaaS & Cloud" if index % 3 == 0 else "Technology" if index % 2 == 0 else "IT Services"

    location = "Bengaluru, India" if index % 3 == 0 else "Mumbai, India" if index % 3 == 1 else "Delhi NCR, India" if index % 5 == 0 else "Pune, India" if index % 4 == 0 else "Hyderabad, India"
    ctc = round(7.5 + (index % 12) * 1.5, 1)
    diff = "Easy" if ctc < 12 else ("Medium" if ctc < 22 else "Hard")
    rule_gpa = round(6.5 + (index % 5) * 0.5, 2)
    
    # Assign actual realistic skills
    if industry == "FinTech":
        skills = [("Java", 4, "Intermediate"), ("PostgreSQL", 4, "Intermediate"), ("REST APIs", 5, "Intermediate")]
    elif industry in ["E-Commerce & Delivery", "E-Commerce & Retail"]:
        skills = [("Node.js", 4, "Intermediate"), ("React", 4, "Intermediate"), ("MongoDB", 4, "Intermediate")]
    elif industry == "Automotive":
        skills = [("C++", 4, "Intermediate"), ("Embedded C", 4, "Intermediate"), ("Git", 3, "Intermediate")]
    elif industry == "SaaS & Cloud":
        skills = [("Python", 4, "Intermediate"), ("FastAPI", 4, "Intermediate"), ("AWS", 4, "Intermediate")]
    else:
        skills = [("Java", 4, "Intermediate"), ("SQL", 4, "Intermediate"), ("Git", 4, "Intermediate")]
    
    ADDITIONAL_COMPANIES.append(
        (name, f"https://www.google.com/search?q={name.replace(' ', '+')}+careers", industry, location, ctc, diff, ["CSE", "IT", "ECE"], rule_gpa, skills)
    )

ALL_COMPANIES = COMPANIES_DATA + ADDITIONAL_COMPANIES

def seed_database():
    db = SessionLocal()
    try:
        print("Clearing existing companies and associated roles/rules...")
        db.query(Company).delete()
        db.commit()
        print("Database cleared successfully.")

        print(f"Start seeding {len(ALL_COMPANIES)} companies with realistic industry patterns...")
        
        for idx, item in enumerate(ALL_COMPANIES):
            name, web, industry, location, ctc, diff, branches, min_gpa, skills = item
            
            # 1. Create Company
            comp = Company(
                name=name,
                website_url=web,
                careers_url=web,
                industry=industry,
                hq_location=location,
                hiring_frequency="Yearly" if idx % 2 == 0 else "Bi-yearly",
                internship_ppo_available=True if idx % 3 != 0 else False,
                remote_onsite="Onsite" if idx % 4 != 0 else "Remote" if idx % 8 == 0 else "Hybrid",
                data_source="Indian Placement Seeder"
            )
            db.add(comp)
            db.commit()
            db.refresh(comp)
            
            # Fetch the matching industry template or default to SDE Technology
            template = ROLE_TEMPLATES.get(industry, ROLE_TEMPLATES["Technology"])
            
            # 2. Create Job Role
            role = CompanyRole(
                company_id=comp.id,
                title=template["title"],
                ctc=ctc,
                description=template["description"],
                application_link=web,
                difficulty=diff,
                selection_rounds=template["selection_rounds"] if "selection_rounds" in template else (3 if idx % 2 == 0 else 4),
                hiring_pattern=template["hiring_pattern"],
                expected_oa_pattern=template["expected_oa_pattern"],
                technical_interview_topics=template["technical_interview_topics"],
                hr_interview_topics=template["hr_interview_topics"],
                interview_experience=template["interview_experience"],
                preparation_resources=template["preparation_resources"]
            )
            db.add(role)
            db.commit()
            db.refresh(role)
            
            # 3. Create Eligibility Rule
            rule = EligibilityRule(
                role_id=role.id,
                min_cgpa=min_gpa,
                allowed_branches=branches,
                max_active_backlogs=0 if idx % 5 != 0 else 1,
                min_resume_match_score=60 if ctc < 12 else 70 if ctc < 22 else 75
            )
            db.add(rule)
            
            # 4. Create Skill Weights
            for sname, weight, lvl in skills:
                db.add(CompanySkillWeight(
                    role_id=role.id,
                    skill_name=sname,
                    importance=weight,
                    required_level=lvl
                ))
            
            db.commit()
            
            if (idx + 1) % 50 == 0:
                print(f"Seeded {idx + 1}/{len(ALL_COMPANIES)} companies...")

        print(f"SUCCESS: Successfully seeded {len(ALL_COMPANIES)} companies!")
    except Exception as e:
        db.rollback()
        print(f"ERROR: Seeding failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
