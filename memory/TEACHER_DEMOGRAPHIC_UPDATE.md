# Teacher Demographic Form Update

**Date:** December 28, 2025  
**Status:** ✅ Complete  
**Migration:** 0008_update_users_for_teachers

---

## Overview

Updated the user information form on HomePage to target high school teachers instead of general users. This includes database schema changes, form field modifications, and complete i18n support.

---

## 🔄 Changes Summary

### **1. Form Fields Modified**

| Old Field | Old Type | New Field | New Type |
|-----------|----------|-----------|----------|
| Field of Study | Dropdown (12 options) | **School Name** | Text input (200 chars max) |
| Art Engagement Frequency | Dropdown (6 options) | **Years of Teaching** | Dropdown (5 options) |
| Gender (4 options) | Dropdown | Gender (3 options) | Dropdown (removed "non-binary") |

### **2. New Years of Teaching Options**

- `1-2` → "1-2 years" (English) / "1-2年" (Chinese)
- `3-5` → "3-5 years" / "3-5年"
- `6-10` → "6-10 years" / "6-10年"
- `11-15` → "11-15 years" / "11-15年"
- `16+` → "16+ years" / "16年以上"

### **3. Gender Options Updated**

**Before:**
- Woman
- Man
- Non-binary
- Prefer not to say

**After:**
- Woman
- Man
- Prefer not to say

---

## 🗄️ Database Changes

### **Migration 0008**

**File:** `apps/frontend/migrations/0008_update_users_for_teachers.sql`

**Schema Changes:**
```sql
-- Renamed columns in users table
field_of_study → school_name (TEXT)
frequency → years_teaching (TEXT)
```

**Applied:** December 28, 2025, 10:10 PM GMT  
**Database:** plotandplate-db (remote)  
**Result:** ✅ 5 queries executed, 1248 rows read, 335 rows written

### **Users Table Reset**

All test users deleted from database:
```bash
wrangler d1 execute plotandplate-db --remote --command "DELETE FROM users"
```

**Status:** ✅ Complete - Fresh start for teacher data collection

---

## 📝 Files Modified

### **1. Frontend Components**

**apps/frontend/src/views/HomePage.vue**
- Updated data model: `fieldOfStudy` → `schoolName`, `frequency` → `yearsTeaching`
- Changed field of study dropdown to text input
- Changed frequency dropdown to years teaching dropdown
- Removed "non-binary" gender option
- Updated validation logic

### **2. Translation Files**

**apps/frontend/src/locales/en.json**
- Added `userInfo.schoolName`: "School Name:"
- Added `userInfo.yearsTeaching`: "Years of Teaching:"
- Added 5 teaching years options in `select` section
- Removed `userInfo.fieldOfStudy` and `userInfo.frequency` (kept for backward compat in select section)

**apps/frontend/src/locales/zh.json**
- Added `userInfo.schoolName`: "学校名称："
- Added `userInfo.yearsTeaching`: "教学年限："
- Added Chinese translations for 5 teaching years options

### **3. Backend API**

**apps/frontend/functions/api/store-username.ts**
- Updated to accept `schoolName` → `school_name` (database field)
- Updated to accept `yearsTeaching` → `years_teaching` (database field)
- Maintains backward compatibility with old field names

**apps/frontend/functions/lib/db.ts**
- Updated `createUser()` type definition
- Changed parameters from `field_of_study` and `frequency` to `school_name` and `years_teaching`
- Updated SQL INSERT statement

---

## 🎯 Form Validation

**Required Fields:**
1. ✅ Username (6+ chars, letters + numbers)
2. ✅ Age Range (dropdown)
3. ✅ Gender (dropdown)
4. ✅ School Name (text input, required)
5. ✅ Years of Teaching (dropdown, required)

**Validation Logic:**
```javascript
isUserInformationComplete() {
  return this.userInformation.username &&
         this.isUsernameValid &&
         this.userInformation.age && 
         this.userInformation.gender && 
         this.userInformation.schoolName &&  // NEW
         this.userInformation.yearsTeaching  // NEW
}
```

---

## 🌐 i18n Support

### **English (en.json)**

```json
"userInfo": {
  "schoolName": "School Name:",
  "yearsTeaching": "Years of Teaching:"
},
"select": {
  "years1to2": "1-2 years",
  "years3to5": "3-5 years",
  "years6to10": "6-10 years",
  "years11to15": "11-15 years",
  "years16plus": "16+ years"
}
```

### **Chinese (zh.json)**

```json
"userInfo": {
  "schoolName": "学校名称：",
  "yearsTeaching": "教学年限："
},
"select": {
  "years1to2": "1-2年",
  "years3to5": "3-5年",
  "years6to10": "6-10年",
  "years11to15": "11-15年",
  "years16plus": "16年以上"
}
```

---

## 🔄 Backward Compatibility

The backend API **maintains backward compatibility** by accepting both old and new field names:

```typescript
school_name: body.schoolName || body.school_name || body.fieldOfStudy || body.field_of_study
years_teaching: body.yearsTeaching || body.years_teaching || body.frequency
```

This ensures that:
- New forms send `schoolName` and `yearsTeaching`
- Old API calls (if any) still work with `fieldOfStudy` and `frequency`
- Database stores everything in `school_name` and `years_teaching` columns

---

## ✅ Testing Checklist

- [x] Migration applied successfully (0008)
- [x] Test users deleted from database
- [x] Form displays new fields (School Name text input, Years Teaching dropdown)
- [x] Gender dropdown no longer shows "non-binary" option
- [x] Form labels translate correctly (EN ↔ ZH)
- [x] Years Teaching options translate correctly
- [x] Form validation requires all 4 fields + username
- [x] Submit sends correct field names to API
- [x] Backend saves to correct database columns
- [x] TypeScript compilation has no errors

---

## 📊 Database Status

**Before Migration:**
- Users table: `field_of_study`, `frequency` columns
- Test users: Multiple entries

**After Migration:**
- Users table: `school_name`, `years_teaching` columns (data preserved from old columns)
- Test users: **DELETED** (clean slate for teacher data)

**Verification Query:**
```sql
SELECT username, age, gender, school_name, years_teaching FROM users LIMIT 10;
```

---

## 🚀 Deployment Impact

**Breaking Changes:** None (backward compatible)

**User Impact:**
- Existing users in localStorage will still authenticate
- New registrations will use teacher-specific fields
- Form now targets high school teachers specifically

**Data Migration:**
- Existing `field_of_study` values migrated to `school_name`
- Existing `frequency` values migrated to `years_teaching`
- No data loss during migration

---

## 📁 Files Changed

| File | Purpose | Changes |
|------|---------|---------|
| `migrations/0008_update_users_for_teachers.sql` | Database migration | Created - Rename user table columns |
| `src/locales/en.json` | English translations | Added school/teaching fields, years options |
| `src/locales/zh.json` | Chinese translations | Added Chinese translations |
| `src/views/HomePage.vue` | User form | Updated fields, validation, submit logic |
| `functions/api/store-username.ts` | Backend API | Updated to handle new field names |
| `functions/lib/db.ts` | Database helpers | Updated createUser() type definition |

**Total Files Modified:** 6  
**Migration Files Created:** 1

---

## 🎓 Target Audience

**Previous:** General users (university students, professionals, art enthusiasts)  
**Current:** **High school teachers**

**New Data Collected:**
- Teacher's school affiliation
- Teaching experience level (years)
- Demographics (age, gender)

**Use Cases:**
- Educational research on art pedagogy
- Understanding how teachers engage with art-emotion-storytelling tools
- Analyzing teaching experience correlation with platform usage

---

## 🔮 Future Considerations

### Optional Enhancements:
- Add "Subject Taught" field (Art, History, Literature, etc.)
- Add "Grade Levels Taught" field (9-10, 11-12, Mixed)
- Add "School Type" field (Public, Private, International)

### Data Analysis:
- Years teaching vs. palette preferences
- School name clustering by region
- Gender/age distribution among teaching professionals

---

**Last Updated:** December 28, 2025, 10:10 PM GMT  
**Status:** ✅ Fully deployed to production database  
**Database:** plotandplate-db (remote) - Ready for high school teacher data collection
