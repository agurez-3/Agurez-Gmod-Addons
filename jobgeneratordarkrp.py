#!/usr/bin/env python3
"""
DarkRP Job Generator for Garry's Mod
Generates DarkRP job definitions based on user input
"""

import json
import os
from datetime import datetime

class DarkRPJobGenerator:
    def __init__(self):
        self.jobs = []
        
    def get_user_input(self, prompt, default=None, required=True):
        """Get user input with optional default value"""
        while True:
            user_input = input(f"{prompt} [{default}]: " if default else f"{prompt}: ").strip()
            if not user_input and default is not None:
                return default
            if user_input or not required:
                return user_input if user_input else None
            print("This field is required!")
    
    def get_validated_int(self, prompt, min_val, max_val, default):
        """Validate integer input within a range"""
        while True:
            value = self.get_user_input(prompt, default)
            try:
                value_int = int(value)
                if min_val <= value_int <= max_val:
                    return value_int
                else:
                    print(f"Value must be between {min_val} and {max_val}!")
            except ValueError:
                print("Invalid input, please enter a number!")
    
    def get_color_input(self):
        """Get RGBA color values"""
        print("\n--- Color Settings ---")
        r = self.get_validated_int("Red (0-255)", 0, 255, "50")
        g = self.get_validated_int("Green (0-255)", 0, 255, "50")
        b = self.get_validated_int("Blue (0-255)", 0, 255, "255")
        a = self.get_validated_int("Alpha (0-255)", 0, 255, "255")
        return f"Color({r}, {g}, {b}, {a})"
    
    def get_models_input(self):
        """Get player models for the job"""
        print("\n--- Player Models ---")
        models = []
        while True:
            model = self.get_user_input("Model path (e.g., models/player/urban.mdl)", required=False)
            if not model:
                if not models:
                    models.append('"models/player/urban.mdl"')
                break
            models.append(f'"{model}"')
            
            if self.get_user_input("Add another model? (y/n)", "n").lower() != 'y':
                break
        
        if len(models) == 1:
            return models[0]
        return "{" + ", ".join(models) + "}"
    
    def get_weapons_input(self):
        """Get weapons for the job"""
        print("\n--- Weapons ---")
        weapons = []
        while True:
            weapon = self.get_user_input("Weapon class (e.g., weapon_pistol)", required=False)
            if not weapon:
                if not weapons:
                    weapons.append('"weapon_pistol"')
                break
            weapons.append(f'"{weapon}"')
            
            if self.get_user_input("Add another weapon? (y/n)", "n").lower() != 'y':
                break
        
        return "{" + ", ".join(weapons) + "}"
    
    def get_spawn_settings(self):
        """Get spawn settings for the job"""
        print("\n--- Spawn Settings ---")
        settings = {}
        
        settings['health'] = int(self.get_user_input("Health", "100"))
        settings['max_health'] = int(self.get_user_input("Max Health", str(settings['health'])))
        settings['armor'] = int(self.get_user_input("Armor", "0"))
        # Automatically set max_armor = armor if empty
        max_armor_input = self.get_user_input("Max Armor (leave empty to match Armor)", str(settings['armor']))
        settings['max_armor'] = int(max_armor_input) if max_armor_input else settings['armor']
        settings['walk_speed'] = int(self.get_user_input("Walk Speed", "200"))
        settings['run_speed'] = int(self.get_user_input("Run Speed", "400"))
        settings['jump_power'] = int(self.get_user_input("Jump Power", "200"))
        
        return settings
    
    def create_job(self):
        """Create a new DarkRP job"""
        print("\n" + "="*50)
        print("NEW DARKRP JOB")
        print("="*50)
        
        # Basic information
        team_name = self.get_user_input("Team Name (e.g., TEAM_SUPER)", "TEAM_CUSTOM").upper()
        job_name = self.get_user_input("Job Name (e.g., Super Soldier)", "Custom Job")
        
        # Color
        color = self.get_color_input()
        
        # Description
        description = self.get_user_input("Description", "A custom DarkRP job")
        description = description.replace('\n', '\\n')
        
        # Models
        models = self.get_models_input()
        
        # Weapons
        weapons = self.get_weapons_input()
        
        # Other settings
        command = self.get_user_input("Chat command", job_name.lower().replace(" ", ""))
        max_players = int(self.get_user_input("Max Players", "2"))
        salary = int(self.get_user_input("Salary", "50"))
        has_license = self.get_user_input("Has license? (y/n)", "y").lower() == 'y'
        vote_required = self.get_user_input("Vote required? (y/n)", "n").lower() == 'y'
        can_demote = self.get_user_input("Can be demoted? (y/n)", "n").lower() == 'y'
        
        # Spawn settings
        spawn_settings = self.get_spawn_settings()
        
        # Generate job code
        job_template = f"""{team_name} = DarkRP.createJob("{job_name}", {{
    color = {color},
    model = {models},
    description = [[{description}]],
    weapons = {weapons},
    command = "{command}",
    max = {max_players},
    salary = {salary},
    admin = 0,
    vote = {str(vote_required).lower()},
    hasLicense = {str(has_license).lower()},
    candemote = {str(can_demote).lower()},

    PlayerSpawn = function(ply)
        ply:SetHealth({spawn_settings['health']})
        ply:SetMaxHealth({spawn_settings['max_health']})
        ply:SetArmor({spawn_settings['armor']})
        ply:SetMaxArmor({spawn_settings['max_armor']})
        ply:SetWalkSpeed({spawn_settings['walk_speed']})
        ply:SetRunSpeed({spawn_settings['run_speed']})
        ply:SetJumpPower({spawn_settings['jump_power']})
    end
}})"""
        
        self.jobs.append({
            'team_name': team_name,
            'job_name': job_name,
            'code': job_template
        })
        
        return job_template
    
    def save_jobs(self):
        """Save all created jobs to a Lua file"""
        if not self.jobs:
            print("No jobs to save!")
            return
            
        filename = f"darkrp_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.lua"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("-- DarkRP Jobs generated with Python Script\n")
            f.write("-- Created on: " + datetime.now().strftime('%d.%m.%Y %H:%M:%S') + "\n\n")
            
            for job in self.jobs:
                f.write(job['code'])
                f.write("\n\n")
        
        print(f"\n✅ Jobs saved to: {filename}")
    
    def show_menu(self):
        """Show main menu"""
        while True:
            print("\n" + "="*50)
            print("DARKRP JOB GENERATOR")
            print("="*50)
            print("1. Create a new job")
            print("2. Show all jobs")
            print("3. Save jobs")
            print("4. Exit")
            print("="*50)
            
            choice = self.get_user_input("Choose an option", "1")
            
            if choice == "1":
                job_code = self.create_job()
                print("\n" + "="*50)
                print("GENERATED CODE:")
                print("="*50)
                print(job_code)
                
            elif choice == "2":
                if not self.jobs:
                    print("No jobs created!")
                else:
                    print("\n" + "="*50)
                    print("CREATED JOBS:")
                    print("="*50)
                    for i, job in enumerate(self.jobs, 1):
                        print(f"{i}. {job['team_name']} - {job['job_name']}")
                        
            elif choice == "3":
                self.save_jobs()
                
            elif choice == "4":
                if self.jobs and self.get_user_input("Save jobs before exiting? (y/n)", "y").lower() == 'y':
                    self.save_jobs()
                print("Goodbye!")
                break
                
            else:
                print("Invalid input!")

def main():
    """Main function"""
    generator = DarkRPJobGenerator()
    
    print("🎮 DarkRP Job Generator for Garry's Mod")
    print("Easily create custom DarkRP jobs with this tool!")
    
    if generator.get_user_input("Do you want to create a job now? (y/n)", "y").lower() == 'y':
        job_code = generator.create_job()
        print("\n" + "="*50)
        print("GENERATED CODE:")
        print("="*50)
        print(job_code)
        
        if generator.get_user_input("Save the job? (y/n)", "y").lower() == 'y':
            generator.save_jobs()
        else:
            generator.show_menu()
    else:
        generator.show_menu()

if __name__ == "__main__":
    main()
