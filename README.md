Project Management Application (PMA)

Overview

This repository showcases the Project Management Application (PMA) developed as a semester-long team project for university. The PMA was designed to streamline project collaboration, integrate user roles with varying access levels, and support cloud storage for file uploads. The project adheres to a set of base and extended requirements while providing opportunities for customization and thematic enhancements.

My Roles

As Scrum Master and Lead UI Designer, I was responsible for:

Scrum Master Duties:

Facilitating team meetings and ensuring the project stayed on schedule.

Monitoring team progress and addressing any roadblocks.

Serving as the primary point of contact for team updates and issues.

Lead UI Designer:

Designing intuitive and user-friendly interfaces for all user roles.

Implementing responsive design principles for seamless usability across devices.

Customizing the application’s theming to align with user needs and enhance visual appeal.

Key Features

Core Functionality

The PMA meets the following base requirements:

Google Account Integration: All regular users log in using their Google accounts, ensuring secure and seamless access.

User Roles:

Anonymous Users: Limited access to view high-level project information.

Common Users: Full project management capabilities, including creating, joining, and managing projects.

PMA Administrators: Oversight capabilities, including viewing and moderating all projects and files.

Django Administrators: Administrative access to the Django admin page.

Project Features:

Title, description, owner, members, and file uploads.

Support for multiple file types (.txt, .pdf, .jpg) stored securely on Amazon S3.

File metadata (e.g., title, timestamp, description, keywords) for efficient organization.

Messaging system for project members to collaborate effectively.

Extended Functionality

To better meet the needs of users, the following customizations were implemented:

User profiles featuring names, Google accounts, join dates, and optional details like profile pictures.

User-friendly interfaces for file and project management, optimized for clarity and accessibility.

Enhanced visual theming to align with the domain of the PMA.

Technical Stack

The PMA was built using the following technologies:

Backend: Python 3, Django 5

Database: PostgreSQL

Frontend: Custom theming with responsive design principles

Cloud Storage: Amazon S3 for file uploads

Hosting: Heroku

Continuous Integration: GitHub Actions

Version Control: GitHub

Contribution Highlights

Leadership

Organized and facilitated weekly sprint meetings.

Maintained team focus on deliverables and milestones.

Ensured compliance with technical requirements and quality standards.

UI Design

Designed and implemented a clean and consistent layout for all pages.

Created accessible navigation flows for all user roles.

Implemented visual feedback mechanisms for better user interaction.

How to Use

Clone the repository:

git clone https://github.com/your-username/project-management-app.git

Set up the environment:

Install dependencies: pip install -r requirements.txt

Configure environment variables for Google API and Amazon S3.

Run the server:

python manage.py runserver

Access the app at http://127.0.0.1:8000/.

Lessons Learned

Team Leadership: Balancing Scrum Master responsibilities with active code contributions taught me effective time management and prioritization.

UI Design: Developing an intuitive interface deepened my understanding of user-centered design principles.

Full-Stack Development: Implementing cloud storage, Google login, and file metadata broadened my technical expertise.

Future Improvements

Adding real-time live chat for better collaboration.

Enhancing file search functionality using advanced metadata tagging.

Further optimizing performance for larger datasets.

Acknowledgments

Thank you to my team members for their collaboration and effort throughout this project. Special thanks to our course instructors for their guidance.

License

This project is for educational purposes only and is not monitored. No real information should be submitted. See the LICENSE file for details.
