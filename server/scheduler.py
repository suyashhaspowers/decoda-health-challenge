from datetime import timedelta
import json
import iso8601

gpt_tools = [
    {
        "type": "function",
        "function": {
            "name": "schedule_appointment",
            "description": "Given a clinic's current schedule and a request for a new appointment, this function will book an appointment for our client if there is no scheduling conflict.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_date": {
                        "type": "string",
                        "description": "The start time that a client wants to book their appointment at. This should be converted to UTC timestamptz format. Recall, UTC is 5 hours ahead of EST."
                    },
                    "duration": {
                        "type": "integer",
                        "description": "The duration of the appointment in minutes."
                    },
                    "title": {
                        "type": "string",
                        "description": "Appointment title"
                    },
                },
                "required": ["appointment_date", "duration"]
            }
        }
    }
]

def save_appointments(appointments):
    with open('appointments.json', 'w') as file:
        json.dump(appointments, file, indent=4)

def load_appointments():
    with open('appointments.json', 'r') as file:
        appointments = json.load(file)
    return appointments

def check_for_conflicts(new_appointment, existing_appointments):
    new_appointment_date = iso8601.parse_date(new_appointment['appointment_date'])
    new_end_time = new_appointment_date + timedelta(minutes=new_appointment['duration'])
    for appointment in existing_appointments:
        appointment_date = iso8601.parse_date(appointment['appointment_date'])
        end_time = appointment_date + timedelta(minutes=appointment['duration'])
        if (new_appointment_date < end_time) and (new_end_time > appointment_date):
            return True  # Conflict found
    return False  # No conflict

def schedule_appointment(new_appointment_args):
    new_appointment = json.loads(new_appointment_args)

    if 'title' not in new_appointment.keys():
        new_appointment['title'] = 'Checkup'

    appointments = load_appointments()

    new_appointment['patient_name'] = f"Patient {len(appointments) + 1}"

    if check_for_conflicts(new_appointment, appointments):
        print("There is a scheduling conflict with existing appointments.")
        return False
    else:
        appointments.append(new_appointment)
        save_appointments(appointments)
        print("Appointment scheduled successfully.")
        return True