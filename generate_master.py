import pandas as pd
import sys

try:
    print("1. Loading files with 'utf-8-sig' encoding...")
    # Read the main and sub CSV files
    df_main = pd.read_csv('03. 표제부_20260528163743.csv', encoding='utf-8-sig') 
    df_sub = pd.read_csv('05. 부속지번_20260528163804.csv', encoding='utf-8-sig')
    print(f"   Loaded main table: {df_main.shape}")
    print(f"   Loaded sub table: {df_sub.shape}")

    print("\n2. Merging dataframes on '관리건축물대장PK' (Left Join)...")
    # Left join on '관리건축물대장PK'
    df_merged = pd.merge(df_sub, df_main, on='관리건축물대장PK', how='left')
    print(f"   Merged shape: {df_merged.shape}")

    print("\n3. Creating 19-digit unique parcel code (PNU)...")
    # PNU structure: Sigungu(5) + Legal Dong(5) + Land Type(1) + Main parcel number(4) + Sub parcel number(4)
    def map_land_type(x):
        if pd.isna(x):
            return '1'
        val = int(x)
        if val == 0:
            return '1'
        elif val == 1:
            return '2'
        else:
            return '1'

    sigungu = df_merged['부속시군구코드'].fillna(0).astype(int).astype(str).str.zfill(5)
    legal_dong = df_merged['부속법정동코드'].fillna(0).astype(int).astype(str).str.zfill(5)
    land_type = df_merged['부속대지구분코드'].map(map_land_type).astype(str).str.zfill(1)
    main_num = df_merged['부속번'].fillna(0).astype(int).astype(str).str.zfill(4)
    sub_num = df_merged['부속지'].fillna(0).astype(int).astype(str).str.zfill(4)

    df_merged['PNU'] = sigungu + legal_dong + land_type + main_num + sub_num
    print("   PNU generated successfully.")

    print("\n4. Extracting key columns for analysis...")
    target_cols = ['PNU', '주용도코드명', '대지면적(㎡)', '건축면적(㎡)', '연면적(㎡)', '용적률(%)', '건폐율(%)']
    df_final = df_merged[target_cols]
    print(f"   Final dataframe shape: {df_final.shape}")

    print("\n5. Saving final master data to '송파구_필지별_건축마스터.csv'...")
    output_filename = '송파구_필지별_건축마스터.csv'
    try:
        df_final.to_csv(output_filename, index=False, encoding='cp949')
        print(f"[SUCCESS] Step 1 Complete: '{output_filename}' file has been created with 'cp949' encoding!")
    except UnicodeEncodeError as e:
        print(f"[WARNING] cp949 encoding failed due to: {e}")
        df_final.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"[SUCCESS] Step 1 Complete: '{output_filename}' file has been created with 'utf-8-sig' encoding!")

except Exception as e:
    print(f"[ERROR] Error occurred: {e}", file=sys.stderr)
    sys.exit(1)
