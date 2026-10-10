# backend/inventory.py
import pandas as pd
from filelock import FileLock

INVENTORY_DB = 'pau_hostel_inventory.csv'
INV_LOCK = 'inventory.lock'

def get_grouped_availability(gender_filter=None):
    df = pd.read_csv(INVENTORY_DB)
    
    if gender_filter:
        df = df[df['Gender'].str.lower() == gender_filter.lower()]
        
    # Group beds by Room to calculate current capacity vs allocated
    room_summary = df.groupby(['Hostel_Name', 'Room_Number', 'Gender', 'Room_Capacity', 'Floors', 'Study_Rooms', 'Cooking_Spaces']).agg(
        Total_Beds=('Bed_ID', 'count'),
        Allocated_Beds=('Is_Allocated', 'sum')
    ).reset_index()
    
    room_summary['Available_Beds'] = room_summary['Total_Beds'] - room_summary['Allocated_Beds']
    return room_summary[room_summary['Available_Beds'] > 0].to_dict(orient='records')

def request_booking(student_id, hostel_name, room_number):
    with FileLock(INV_LOCK):
        # df = pd.read_csv(INVENTORY_DB)
        df = pd.read_csv(INVENTORY_DB, dtype={'Allocated_StudentID': str})
        # Check if student already has a bed
        if (df['Allocated_StudentID'] == str(student_id)).any():
            return False, "Student already has an allocated bed."
            
        # Find first unallocated bed in the target room
        mask = (df['Hostel_Name'] == hostel_name) & (df['Room_Number'] == room_number) & (~df['Is_Allocated'])
        available_beds = df[mask]
        
        if available_beds.empty:
            return False, "Room is fully booked."
            
        target_index = available_beds.index[0]
        bed_id = df.at[target_index, 'Bed_ID']
        
        # Set allocation as pending (For MVP, we mark allocated, in full app this goes to a separate bookings CSV for admin approval)
        df.at[target_index, 'Is_Allocated'] = True
        df.at[target_index, 'Allocated_StudentID'] = str(student_id)
        
        df.to_csv(INVENTORY_DB, index=False)
        return True, f"Bed {bed_id} successfully booked."