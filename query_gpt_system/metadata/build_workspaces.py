import json

# Định nghĩa danh sách các workspace và file tương ứng
workspace_data = {
    "finance": {
        "description": "Tài chính, ngân hàng, chứng khoán, lương, kinh tế",
        "tables": [
            "tr_eikon_eod_data.csv", "bitconnect_price.csv", "GODREJIND.csv", "e5_aapl.csv", 
            "Credit.csv", "cs-test.csv", "YAHOO-BTC_USD_D.csv", "microsoft.csv", 
            "random_stock_data.csv", "credit-data-post-import.csv", "2014_q4.csv", 
            "2015.csv", "Baltimore_City_Employee_Salaries_FY2013.csv", 
            "city_departments_in_current_budget.csv", "cost_data_with_errors.csv", 
            "unemployement_industry.csv", "beauty%20and%20the%20labor%20market.csv"
        ]
    },
    "health": {
        "description": "Y tế, sức khỏe, bệnh viện, bảo hiểm, sinh học",
        "tables": [
            "ferret-Pitt-2-preinf-lib2-100_sitediffsel.csv", "country_vaccinations.csv", 
            "insurance.csv", "imp.score.ldlr.metabolome.csv", "cms_hospital_readmissions.csv", 
            "abalone.csv", "tree.csv"
        ]
    },
    "transportation": {
        "description": "Giao thông, vận tải, phương tiện di chuyển",
        "tables": [
            "traj-Osak.csv", "bike_rental_hour.csv", "auto-mpg.csv", 
            "titanic.csv", "titanic_train.csv", "titanic_test.csv"
        ]
    },
    "sports": {
        "description": "Thể thao, bóng đá, bóng chày, trò chơi, giải trí",
        "tables": [
            "vgsales.csv", "baseball_data.csv", "fb_articles_20180822_20180829_df.csv", 
            "Todo_Tango_letras_final.csv"
        ]
    },
    "general": {
        "description": "Thời tiết, nhân khẩu học, bất động sản và các dữ liệu chung khác",
        "tables": [
            "gapminder_cleaned.csv", "weather_train.csv", "oecd_education_spending.csv", 
            "baro_2015.csv", "weather_data_1864.csv", "Zip_MedianSoldPricePerSqft_AllHomes.csv", 
            "election2016.csv", "percent-bachelors-degrees-women-usa.csv", "census.csv", 
            "arrest_expungibility.csv", "housedata.csv", "gapminder_gdp_asia.csv", 
            "Current_Logan.csv", "ravenna_250715.csv", "train_new_ocr_29.csv", "2015-09-21.csv", 
            "veracruz%202016.csv", "diamonds.csv", "0020200722.csv", 
            "20170413_000000_group_statistics.csv", "test_Y3wMUE5_7gLdaTN.csv", "test_ave.csv", 
            "3901.csv", "Gillam_fin.csv", "Yelp_Reviews.csv", "estimated_numbers.csv", 
            "well_2_complete.csv", "2019-08_edges.csv", "ts-sc4-wi100000-sl25000-Qrob_Chr05.tree_table.csv", 
            "test_x.csv", "api_output_2018-09-11_11-08-28.csv", "hotel_data.csv", 
            "DES%3D%2B2006261.csv", "my_test_01.csv"
        ]
    }
}

if __name__ == "__main__":
    with open('query_gpt_system/metadata/workspaces.json', 'w', encoding='utf-8') as f:
        json.dump(workspace_data, f, indent=4, ensure_ascii=False)
    print("Đã tạo file workspaces.json thành công!")
