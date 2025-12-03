import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from election_results.models import PollingUnit, Ward, LGA, State, Party, AnnouncedPuResults, AnnouncedLgaResults

class Command(BaseCommand):
    help = 'Imports data from bincom_test.sql'

    def handle(self, *args, **kwargs):
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        AnnouncedLgaResults.objects.all().delete()
        AnnouncedPuResults.objects.all().delete()
        PollingUnit.objects.all().delete()
        Ward.objects.all().delete()
        LGA.objects.all().delete()
        State.objects.all().delete()
        Party.objects.all().delete()

        file_path = 'bincom_test.sql'
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Helper to parse values
        def parse_values(values_str):
            rows = []
            
            # Remove the leading `(` and trailing `);` or `)`
            values_str = values_str.strip()
            if values_str.endswith(';'):
                values_str = values_str[:-1]
            
            # Split by "), (" handling newlines
            # Use regex to split by ), followed by whitespace/newlines, followed by (
            raw_rows = re.split(r'\),\s*\(', values_str)
            
            parsed_rows = []
            for raw_row in raw_rows:
                # Fix leading/trailing parens for first/last items
                if raw_row.startswith('('):
                    raw_row = raw_row[1:]
                if raw_row.endswith(')'):
                    raw_row = raw_row[:-1]
                
                # Now split fields by comma, respecting quotes
                fields = []
                current_field = ''
                in_quote = False
                escape = False
                
                for char in raw_row:
                    if escape:
                        current_field += char
                        escape = False
                        continue
                    
                    if char == '\\':
                        escape = True
                        # current_field += char # Don't add backslash if it's escaping
                        continue
                        
                    if char == "'" and not escape:
                        in_quote = not in_quote
                        # current_field += char # Keep quotes? No, strip them later or keep them to identify strings
                        continue
                    
                    if char == ',' and not in_quote:
                        fields.append(current_field.strip())
                        current_field = ''
                    else:
                        current_field += char
                
                fields.append(current_field.strip())
                
                # Clean up fields
                clean_fields = []
                for field in fields:
                    if field.upper() == 'NULL':
                        clean_fields.append(None)
                    elif field.startswith("'") and field.endswith("'"):
                        clean_fields.append(field[1:-1]) # Remove quotes
                    elif field.isdigit():
                        clean_fields.append(int(field))
                    else:
                        # Try float
                        try:
                            clean_fields.append(float(field))
                        except ValueError:
                            clean_fields.append(field) # Keep as string
                
                parsed_rows.append(clean_fields)
            return parsed_rows

        # Process INSERT statements
        insert_pattern = re.compile(r'INSERT INTO `(\w+)` \((.*?)\) VALUES\s*(.*?);', re.DOTALL | re.IGNORECASE)
        
        # The file might have multiple inserts for the same table, or one huge insert.
        # The regex might fail on huge content. Let's iterate line by line or chunks?
        # The dump seems to have one INSERT per table or chunks.
        # Let's try matching all.
        
        matches = insert_pattern.findall(content)
        
        for table, columns, values in matches:
            self.stdout.write(f"Processing table: {table}")
            rows = parse_values(values)
            
            # Map columns to model fields
            # columns is like "`id`, `name`"
            cols = [c.strip('` ') for c in columns.split(',')]
            
            if table == 'polling_unit':
                for row in rows:
                    data = dict(zip(cols, row))
                    # Handle date_entered if present
                    if 'date_entered' in data and data['date_entered']:
                         # Format is usually 'YYYY-MM-DD HH:MM:SS'
                         pass
                    
                    PollingUnit.objects.create(
                        uniqueid=data.get('uniqueid'),
                        polling_unit_id=data.get('polling_unit_id'),
                        ward_id=data.get('ward_id'),
                        lga_id=data.get('lga_id'),
                        uniquewardid=data.get('uniquewardid'),
                        polling_unit_number=data.get('polling_unit_number'),
                        polling_unit_name=data.get('polling_unit_name'),
                        polling_unit_description=data.get('polling_unit_description'),
                        lat=data.get('lat'),
                        long=data.get('long'),
                        entered_by_user=data.get('entered_by_user'),
                        user_ip_address=data.get('user_ip_address'),
                        # Skip date_entered for now to avoid parsing errors if format varies, or try parse
                    )

            elif table == 'ward':
                for row in rows:
                    data = dict(zip(cols, row))
                    Ward.objects.create(
                        uniqueid=data.get('uniqueid'),
                        ward_id=data.get('ward_id'),
                        ward_name=data.get('ward_name'),
                        lga_id=data.get('lga_id'),
                        ward_description=data.get('ward_description'),
                        entered_by_user=data.get('entered_by_user'),
                        user_ip_address=data.get('user_ip_address'),
                    )

            elif table == 'lga':
                for row in rows:
                    data = dict(zip(cols, row))
                    LGA.objects.create(
                        uniqueid=data.get('uniqueid'),
                        lga_id=data.get('lga_id'),
                        lga_name=data.get('lga_name'),
                        state_id=data.get('state_id'),
                        lga_description=data.get('lga_description'),
                        entered_by_user=data.get('entered_by_user'),
                        user_ip_address=data.get('user_ip_address'),
                    )

            elif table == 'states':
                for row in rows:
                    data = dict(zip(cols, row))
                    State.objects.create(
                        state_id=data.get('state_id'),
                        state_name=data.get('state_name'),
                    )

            elif table == 'party':
                for row in rows:
                    data = dict(zip(cols, row))
                    Party.objects.create(
                        id=data.get('id'),
                        partyid=data.get('partyid'),
                        partyname=data.get('partyname'),
                    )

            elif table == 'announced_pu_results':
                for row in rows:
                    data = dict(zip(cols, row))
                    # Need to handle date_entered
                    dt = data.get('date_entered')
                    if dt == '0000-00-00 00:00:00':
                        dt = None
                    
                    AnnouncedPuResults.objects.create(
                        result_id=data.get('result_id'),
                        polling_unit_uniqueid=data.get('polling_unit_uniqueid'),
                        party_abbreviation=data.get('party_abbreviation'),
                        party_score=data.get('party_score'),
                        entered_by_user=data.get('entered_by_user'),
                        date_entered=dt,
                        user_ip_address=data.get('user_ip_address'),
                    )

            elif table == 'announced_lga_results':
                for row in rows:
                    data = dict(zip(cols, row))
                    dt = data.get('date_entered')
                    if dt == '0000-00-00 00:00:00':
                        dt = None

                    AnnouncedLgaResults.objects.create(
                        result_id=data.get('result_id'),
                        lga_name=data.get('lga_name'),
                        party_abbreviation=data.get('party_abbreviation'),
                        party_score=data.get('party_score'),
                        entered_by_user=data.get('entered_by_user'),
                        date_entered=dt,
                        user_ip_address=data.get('user_ip_address'),
                    )

        self.stdout.write(self.style.SUCCESS('Successfully imported data'))
