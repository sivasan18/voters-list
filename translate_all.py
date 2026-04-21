import json
import glob
import time
from deep_translator import GoogleTranslator

def translate_batch(translator, names_list):
    # Deep translator handles up to 5000 chars
    # Batch them into chunks of 100
    batch_size = 100
    translated_dict = {}
    
    for i in range(0, len(names_list), batch_size):
        batch = names_list[i:i+batch_size]
        text_to_translate = '\n'.join(batch)
        print(f"Translating batch {i//batch_size + 1}/{len(names_list)//batch_size + 1}...")
        
        retries = 3
        while retries > 0:
            try:
                translated_text = translator.translate(text_to_translate)
                # Split back
                t_list = translated_text.split('\n')
                # Sometime google translate messes up newlines or merges them.
                # To be safe against newlines disappearing:
                if len(t_list) == len(batch):
                    for src, tgt in zip(batch, t_list):
                        translated_dict[src] = tgt.strip()
                else:
                    # Fallback single translation if batch drops lines
                    print("Row count mismatch, translating one by one.")
                    for src in batch:
                        try:
                            t_single = translator.translate(src)
                            translated_dict[src] = t_single.strip() if t_single else ""
                            time.sleep(0.1)
                        except Exception as inner_e:
                            translated_dict[src] = ""
                break
            except Exception as e:
                print(f"Error: {e}. Retrying...")
                retries -= 1
                time.sleep(2)
        
        time.sleep(0.5) # small delay between batches
        
    return translated_dict

def main():
    files = glob.glob('./data/part-*.json')
    translator = GoogleTranslator(source='en', target='ta')
    
    unique_names = set()
    
    # Pass 1: Collect unique names
    for f in files:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            for row in data:
                n = str(row.get('name', ''))
                pn = str(row.get('parent_name', ''))
                # Just take the english part, strip pipes and whitespace
                n_clean = n.replace('|', '').strip()
                pn_clean = pn.replace('|', '').strip()
                if n_clean: unique_names.add(n_clean)
                if pn_clean: unique_names.add(pn_clean)
                
    names_list = list(unique_names)
    print(f"Total unique names to translate: {len(names_list)}")
    
    # Translate
    trans_map = translate_batch(translator, names_list)
    print("Translation complete. Applying to files...")
    
    # Apply and Save
    for f in files:
        print(f"Processing {f}...")
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            
        new_data = []
        for row in data:
            n = str(row.get('name', ''))
            pn = str(row.get('parent_name', ''))
            n_clean = n.replace('|', '').strip()
            pn_clean = pn.replace('|', '').strip()
            
            t_n = trans_map.get(n_clean, '')
            t_pn = trans_map.get(pn_clean, '')
            
            # Exact key order required:
            new_row = {
                "serial_number": row.get('serial_number', ''),
                "part_number": row.get('part_number', ''),
                "name": row.get('name', ''),
                "name_tamil": t_n,
                "epic": row.get('epic', ''),
                "parent_name": row.get('parent_name', ''),
                "parent_name_tamil": t_pn,
                "house_number": row.get('house_number', ''),
                "street_name": row.get('street_name', ''),
                "age": row.get('age', ''),
                "gender": row.get('gender', ''),
                "status": row.get('status', 'active')
            }
            if 'nameLow' in row:
                new_row['nameLow'] = row['nameLow']
            new_data.append(new_row)
            
        with open(f, 'w', encoding='utf-8') as fp:
            json.dump(new_data, fp, indent=2, ensure_ascii=False)
            
    print("Done!")

if __name__ == "__main__":
    main()
