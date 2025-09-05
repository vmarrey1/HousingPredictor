# UC Berkeley Four Year Plan Generator

A comprehensive web application that helps UC Berkeley students create personalized four-year academic plans based on their major and graduation timeline.

## 🎯 Features

- **Major Selection**: Choose from available UC Berkeley majors
- **Graduation Timeline**: Set your expected graduation year
- **Smart Planning**: Automatically generates semester-by-semester course schedules
- **Course Options**: Select from multiple courses that fulfill the same requirements
- **Visual Schedule**: Beautiful, interactive display of your four-year plan
- **Real-time Updates**: Modify your plan and see changes instantly
- **CSV Integration**: Uses real Berkeley course data from CSV files

## 🚀 Tech Stack

### Backend (Python Flask)
- **Flask**: Web framework with CORS support
- **Pandas**: Data processing for course information
- **CSV Integration**: Reads Berkeley course data from CSV files

### Frontend (Next.js TypeScript)
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Modern, responsive styling
- **Framer Motion**: Smooth animations and transitions
- **Lucide React**: Beautiful icons
- **Axios**: HTTP client for API communication

## 📁 Project Structure

```
├── backend/
│   ├── app.py              # Flask application with all API endpoints
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── page.tsx        # Main landing page
│   │   ├── schedule/
│   │   │   └── page.tsx    # Schedule display page
│   │   ├── layout.tsx      # Root layout
│   │   └── globals.css     # Global styles
│   ├── package.json        # Node.js dependencies
│   ├── tailwind.config.js  # Tailwind configuration
│   └── tsconfig.json       # TypeScript configuration
└── README.md               # This file
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Start the Flask server:
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📊 Data Sources

The application uses real UC Berkeley course data from CSV files:
- **Course Information**: Subject, number, title, units, terms offered
- **Major Requirements**: Lower division, upper division, and breadth requirements
- **Academic Policies**: Unit requirements, graduation timelines

## 🎨 User Interface

### Main Page
- **Major Selection**: Dropdown with available majors
- **Graduation Year**: Select your expected graduation year
- **Generate Button**: Creates your personalized four-year plan

### Schedule Page
- **Semester View**: Grid layout showing all 8 semesters
- **Course Details**: Click on semesters to see detailed course information
- **Course Options**: Select from alternative courses for each requirement
- **Visual Indicators**: Color-coded requirement types and terms

## 🔧 API Endpoints

### Backend API

- `GET /api/health` - Health check
- `GET /api/majors` - Get list of available majors
- `GET /api/major/<major_name>` - Get details for a specific major
- `POST /api/generate-plan` - Generate a four-year plan
- `POST /api/course-options` - Get course options for a requirement

### Request Examples

**Generate Four Year Plan:**
```json
POST /api/generate-plan
{
  "major": "Computer Science",
  "graduation_year": 2028,
  "preferences": {}
}
```

**Get Course Options:**
```json
POST /api/course-options
{
  "major": "Computer Science",
  "requirement_type": "lower_division",
  "requirement_name": "Programming Fundamentals"
}
```

## 🎯 How It Works

1. **Data Loading**: The backend loads course data from CSV files and major requirements
2. **Plan Generation**: Creates a four-year timeline based on major requirements
3. **Course Distribution**: Distributes courses across semesters following prerequisites
4. **Interactive Display**: Frontend shows the plan with options to customize
5. **Course Selection**: Users can choose from multiple courses for each requirement

## 🎨 Design Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Clean, professional interface with smooth animations
- **Color Coding**: Different colors for terms (Fall, Spring, Summer) and requirement types
- **Interactive Elements**: Hover effects, loading states, and smooth transitions
- **Accessibility**: Proper contrast ratios and keyboard navigation

## 🔮 Future Enhancements

- **Prerequisite Checking**: Validate course prerequisites
- **Unit Balancing**: Ensure balanced unit loads per semester
- **Elective Suggestions**: Recommend interesting electives
- **Export Options**: Download plans as PDF or calendar files
- **Social Features**: Share plans with advisors or friends
- **Advanced Filtering**: Filter courses by difficulty, time, or instructor

## 🚀 Getting Started

1. **Clone the repository**
2. **Set up both backend and frontend** (see setup instructions above)
3. **Open your browser** to `http://localhost:3000`
4. **Select your major** and graduation year
5. **Generate your plan** and explore the interactive schedule
6. **Customize courses** by clicking on individual semesters

## 📝 Notes

- The application uses sample data for demonstration purposes
- Real course data can be loaded from Berkeley's official CSV files
- Plans are generated based on typical major requirements
- Users can customize their plans by selecting different course options

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please respect UC Berkeley's data usage policies when using real course data.

---

**Happy Planning! 🎓**

Create your perfect four-year journey at UC Berkeley with this comprehensive planning tool.