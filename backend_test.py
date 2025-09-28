#!/usr/bin/env python3
"""
Backend API Testing for Fitness App
Tests all backend endpoints with realistic fitness data
"""

import requests
import json
from datetime import datetime, timezone
import uuid

# Backend URL from environment
BACKEND_URL = "https://shapedaily.preview.emergentagent.com/api"

def test_api_root():
    """Test the root API endpoint"""
    print("🔍 Testing API Root...")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_exercises_api():
    """Test exercise endpoints"""
    print("\n🏋️ Testing Exercise API endpoints...")
    
    # Test GET /exercises
    print("Testing GET /exercises...")
    try:
        response = requests.get(f"{BACKEND_URL}/exercises")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            exercises = response.json()
            print(f"Found {len(exercises)} exercises")
            
            # Verify we have the 5 expected exercises
            expected_exercises = [
                "Push-up",
                "Russian Twist", 
                "Mountain Climber",
                "Elevación de piernas y crunch abdominal",
                "Peso muerto con mancuernas"
            ]
            
            exercise_names = [ex['name'] for ex in exercises]
            print(f"Exercise names: {exercise_names}")
            
            # Check if all expected exercises are present
            missing_exercises = [ex for ex in expected_exercises if ex not in exercise_names]
            if missing_exercises:
                print(f"❌ Missing exercises: {missing_exercises}")
                return False
            
            # Verify YouTube URLs are present
            for exercise in exercises:
                if not exercise.get('video_url') or 'youtube.com' not in exercise['video_url']:
                    print(f"❌ Exercise {exercise['name']} missing valid YouTube URL")
                    return False
                print(f"✅ {exercise['name']}: {exercise['video_url']}")
            
            # Test GET /exercises/{id} with first exercise
            if exercises:
                first_exercise_id = exercises[0]['id']
                print(f"\nTesting GET /exercises/{first_exercise_id}...")
                
                detail_response = requests.get(f"{BACKEND_URL}/exercises/{first_exercise_id}")
                print(f"Status: {detail_response.status_code}")
                
                if detail_response.status_code == 200:
                    exercise_detail = detail_response.json()
                    print(f"✅ Exercise detail: {exercise_detail['name']}")
                    return True
                else:
                    print(f"❌ Failed to get exercise detail: {detail_response.text}")
                    return False
            
        else:
            print(f"❌ Failed to get exercises: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing exercises: {e}")
        return False

def test_workout_sessions_api():
    """Test workout session endpoints"""
    print("\n💪 Testing Workout Session API...")
    
    # Test POST /workouts - Create a workout session
    print("Testing POST /workouts...")
    try:
        workout_data = {
            "date": datetime.now(timezone.utc).isoformat(),
            "exercises_completed": [
                {
                    "exercise_id": "test-exercise-1",
                    "exercise_name": "Push-up",
                    "duration": 30,
                    "repetitions": 15,
                    "sets": 3
                },
                {
                    "exercise_id": "test-exercise-2", 
                    "exercise_name": "Russian Twist",
                    "duration": 45,
                    "repetitions": 20,
                    "sets": 3
                }
            ],
            "total_duration": 300,  # 5 minutes
            "difficulty_rating": 4,
            "energy_level": 3,
            "notes": "Great workout session, felt energized!"
        }
        
        response = requests.post(f"{BACKEND_URL}/workouts", json=workout_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            created_workout = response.json()
            print(f"✅ Created workout session: {created_workout['id']}")
            workout_id = created_workout['id']
        else:
            print(f"❌ Failed to create workout: {response.text}")
            return False
            
        # Test GET /workouts
        print("\nTesting GET /workouts...")
        response = requests.get(f"{BACKEND_URL}/workouts")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            workouts = response.json()
            print(f"✅ Found {len(workouts)} workout sessions")
            
            # Verify our created workout is in the list
            found_workout = any(w['id'] == workout_id for w in workouts)
            if not found_workout:
                print("❌ Created workout not found in list")
                return False
        else:
            print(f"❌ Failed to get workouts: {response.text}")
            return False
            
        # Test GET /workouts/stats
        print("\nTesting GET /workouts/stats...")
        response = requests.get(f"{BACKEND_URL}/workouts/stats")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Workout stats: {stats}")
            
            # Verify stats structure
            required_fields = ['total_sessions', 'recent_sessions', 'total_workout_time', 'average_session_time']
            for field in required_fields:
                if field not in stats:
                    print(f"❌ Missing field in stats: {field}")
                    return False
            
            return True
        else:
            print(f"❌ Failed to get workout stats: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing workout sessions: {e}")
        return False

def test_user_profile_api():
    """Test user profile endpoints"""
    print("\n👤 Testing User Profile API...")
    
    # Test POST /profile - Create/update profile
    print("Testing POST /profile...")
    try:
        profile_data = {
            "height": 175.0,  # cm
            "weight": 70.5,   # kg
            "age": 28,
            "gender": "male",
            "fitness_level": "intermediate",
            "goals": ["lose_weight", "build_muscle", "improve_endurance"],
            "available_equipment": ["dumbbells", "mat", "resistance_bands"],
            "preferred_duration": 30  # minutes
        }
        
        response = requests.post(f"{BACKEND_URL}/profile", json=profile_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            created_profile = response.json()
            print(f"✅ Created/updated profile: {created_profile['id']}")
        else:
            print(f"❌ Failed to create profile: {response.text}")
            return False
            
        # Test GET /profile
        print("\nTesting GET /profile...")
        response = requests.get(f"{BACKEND_URL}/profile")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            profile = response.json()
            if profile:
                print(f"✅ Retrieved profile: Age {profile['age']}, Height {profile['height']}cm")
                
                # Verify profile data matches what we sent
                if profile['height'] != profile_data['height']:
                    print(f"❌ Height mismatch: expected {profile_data['height']}, got {profile['height']}")
                    return False
                    
                return True
            else:
                print("❌ No profile found")
                return False
        else:
            print(f"❌ Failed to get profile: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing user profile: {e}")
        return False

def test_measurements_api():
    """Test measurements endpoints"""
    print("\n📏 Testing Measurements API...")
    
    # Test POST /measurements - Add abdominal measurement
    print("Testing POST /measurements...")
    try:
        measurement_data = {
            "measurement": 85.5,  # cm
            "date": datetime.now(timezone.utc).isoformat(),
            "notes": "Medición después del entrenamiento matutino"
        }
        
        response = requests.post(f"{BACKEND_URL}/measurements", json=measurement_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            created_measurement = response.json()
            print(f"✅ Added measurement: {created_measurement['measurement']}cm")
            measurement_id = created_measurement['id']
        else:
            print(f"❌ Failed to add measurement: {response.text}")
            return False
            
        # Add another measurement for better testing
        measurement_data2 = {
            "measurement": 84.8,  # cm - showing progress
            "date": datetime.now(timezone.utc).isoformat(),
            "notes": "Progreso después de 2 semanas de entrenamiento"
        }
        
        response = requests.post(f"{BACKEND_URL}/measurements", json=measurement_data2)
        if response.status_code != 200:
            print(f"❌ Failed to add second measurement: {response.text}")
            return False
            
        # Test GET /measurements
        print("\nTesting GET /measurements...")
        response = requests.get(f"{BACKEND_URL}/measurements")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            measurements = response.json()
            print(f"✅ Found {len(measurements)} measurements")
            
            # Verify our measurements are in the list
            measurement_values = [m['measurement'] for m in measurements]
            if 85.5 not in measurement_values or 84.8 not in measurement_values:
                print("❌ Created measurements not found in list")
                return False
                
            # Show progress tracking
            print(f"Measurements: {measurement_values}")
            return True
        else:
            print(f"❌ Failed to get measurements: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing measurements: {e}")
        return False

def run_all_tests():
    """Run all backend API tests"""
    print("🚀 Starting Fitness App Backend API Tests")
    print("=" * 50)
    
    test_results = {
        "API Root": test_api_root(),
        "Exercise API": test_exercises_api(),
        "Workout Sessions API": test_workout_sessions_api(),
        "User Profile API": test_user_profile_api(),
        "Measurements API": test_measurements_api()
    }
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    print(f"OVERALL: {overall_status}")
    
    return test_results

if __name__ == "__main__":
    run_all_tests()