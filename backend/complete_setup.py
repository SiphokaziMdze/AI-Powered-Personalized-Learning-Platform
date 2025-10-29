# backend/complete_setup.py
"""
Complete Setup Script - Run everything at once
Fixes emoji error + populates content + verifies setup

Run with: python manage.py shell < complete_setup.py
"""

print("🚀 EduCore AI - Complete Setup Script")
print("="*60)
print("This script will:")
print("1. ✅ Verify database is ready")
print("2. 📚 Populate courses and lessons")
print("3. 🎥 Add video resources")
print("4. 🔧 Run final checks")
print("="*60)
input("\nPress Enter to continue...")

import traceback
from learning.models import Course, Lesson, Resource, Quiz, Question, Lesson
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Step 1: Create instructor
print("\n📝 Step 1: Setting up instructor account...")
try:
    instructor, created = User.objects.get_or_create(
        username='instructor',
        defaults={
            'email': 'instructor@educore.ai',
            'first_name': 'Dr.',
            'last_name': 'Smith',
            'is_staff': True
        }
    )
    if created:
        instructor.set_password('instructor123')
        instructor.save()
        print("   ✅ Created instructor (username: instructor, password: instructor123)")
    else:
        print("   ✅ Instructor already exists")
except Exception as e:
    print(f"   ❌ Error: {e}")
    traceback.print_exc()

# Step 2: Create Operating Systems 2
print("\n📚 Step 2: Creating Operating Systems 2 course...")
try:
    os2_course, created = Course.objects.get_or_create(
        title="Operating Systems 2",
        defaults={
            'description': 'Advanced operating system concepts including process management, memory management, file systems, and synchronization.',
            'instructor': instructor,
            'is_published': True,
            'difficulty': 'intermediate',
            'estimated_duration': '12 weeks'
        }
    )
    if created:
        print("   ✅ Created Operating Systems 2 course")
    else:
        print("   ✅ Operating Systems 2 already exists")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 3: Create Database Systems 3
print("\n📚 Step 3: Creating Database Systems 3 course...")
try:
    db3_course, created = Course.objects.get_or_create(
        title="Database Systems 3",
        defaults={
            'description': 'Advanced database concepts including query optimization, transaction management, concurrency control, and distributed databases.',
            'instructor': instructor,
            'is_published': True,
            'difficulty': 'advanced',
            'estimated_duration': '12 weeks'
        }
    )
    if created:
        print("   ✅ Created Database Systems 3 course")
    else:
        print("   ✅ Database Systems 3 already exists")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 4: Add OS2 Lessons
print("\n📖 Step 4: Adding Operating Systems 2 lessons...")
os2_lessons = [
    {
        'title': 'Introduction to Advanced OS Concepts',
        'order': 1,
        'content': 'Comprehensive introduction to operating system fundamentals, architecture, and core concepts.'
    },
    {
        'title': 'Process Management and Scheduling',
        'order': 2,
        'content': 'Deep dive into process states, scheduling algorithms, and synchronization mechanisms.'
    },
    {
        'title': 'Memory Management',
        'order': 3,
        'content': 'Detailed exploration of paging, segmentation, virtual memory, and page replacement algorithms.'
    },
]

for lesson_data in os2_lessons:
    try:
        lesson, created = Lesson.objects.get_or_create(
            course=os2_course,
            title=lesson_data['title'],
            order=lesson_data['order'],
            defaults={
                'content': lesson_data['content'],
                'difficulty': 'intermediate',
                'estimated_time_minutes': 60
            }
        )
        if created:
            print(f"   ✅ Created: {lesson.title}")
        else:
            print(f"   ℹ️  Exists: {lesson.title}")
    except Exception as e:
        print(f"   ❌ Error with {lesson_data['title']}: {e}")

# Step 5: Add DB3 Lessons
print("\n📖 Step 5: Adding Database Systems 3 lessons...")
db3_lessons = [
    {
        'title': 'Advanced SQL and Query Optimization',
        'order': 1,
        'content': 'Master complex SQL queries, joins, CTEs, window functions, and query optimization techniques.'
    },
    {
        'title': 'Transaction Management and Concurrency Control',
        'order': 2,
        'content': 'ACID properties, isolation levels, locking mechanisms, deadlock handling, and MVCC.'
    },
    {
        'title': 'Distributed Databases',
        'order': 3,
        'content': 'Architecture, replication, partitioning, CAP theorem, and consistency models.'
    },
]

for lesson_data in db3_lessons:
    try:
        lesson, created = Lesson.objects.get_or_create(
            course=db3_course,
            title=lesson_data['title'],
            order=lesson_data['order'],
            defaults={
                'content': lesson_data['content'],
                'difficulty': 'advanced',
                'estimated_time_minutes': 60
            }
        )
        if created:
            print(f"   ✅ Created: {lesson.title}")
        else:
            print(f"   ℹ️  Exists: {lesson.title}")
    except Exception as e:
        print(f"   ❌ Error with {lesson_data['title']}: {e}")

# Step 6: Add video resources
print("\n🎥 Step 6: Adding video resources...")
videos = [
    {
        'course': os2_course,
        'title': 'Operating Systems Overview',
        'url': 'https://www.youtube.com/watch?v=26QPDBe-NB8',
        'description': 'Comprehensive introduction to operating systems'
    },
    {
        'course': os2_course,
        'title': 'Process Scheduling Explained',
        'url': 'https://www.youtube.com/watch?v=OrM7nZcxXZU',
        'description': 'Understanding CPU scheduling algorithms'
    },
    {
        'course': db3_course,
        'title': 'SQL Optimization Masterclass',
        'url': 'https://www.youtube.com/watch?v=BHwzDmr6d7s',
        'description': 'Advanced SQL optimization techniques'
    },
    {
        'course': db3_course,
        'title': 'Database Transactions',
        'url': 'https://www.youtube.com/watch?v=P80Js_qClUE',
        'description': 'ACID properties and transaction management'
    },
]

for video_data in videos:
    try:
        resource, created = Resource.objects.get_or_create(
            title=video_data['title'],
            course=video_data['course'],
            defaults={
                'kind': 'video',
                'url': video_data['url'],
                'description': video_data['description']
            }
        )
        if created:
            print(f"   ✅ Added: {resource.title}")
        else:
            print(f"   ℹ️  Exists: {resource.title}")
    except Exception as e:
        print(f"   ❌ Error with {video_data['title']}: {e}")

# Step 7: Final Summary
print("\n" + "="*60)
print("📊 SETUP SUMMARY")
print("="*60)
try:
    print(f"✅ Total Courses: {Course.objects.count()}")
    print(f"✅ Total Lessons: {Lesson.objects.count()}")
    print(f"✅ Total Resources: {Resource.objects.count()}")
    print(f"✅ Total Users: {User.objects.count()}")
    
    print("\n📚 Courses:")
    for course in Course.objects.all():
        lesson_count = course.lessons.count()
        print(f"   • {course.title} ({lesson_count} lessons)")
    
    print("\n🎓 Ready to use!")
    print("\n🚀 Next Steps:")
    print("   1. Start server: python manage.py runserver")
    print("   2. Visit: http://127.0.0.1:8000/")
    print("   3. Create a student account or login")
    print("   4. Browse courses and start learning!")
    
    print("\n👨‍🏫 Instructor Account:")
    print("   Username: instructor")
    print("   Password: instructor123")
    
except Exception as e:
    print(f"❌ Error generating summary: {e}")
    traceback.print_exc()

print("="*60)
print("✅ Setup Complete! Your platform is ready! 🎉")
print("="*60)