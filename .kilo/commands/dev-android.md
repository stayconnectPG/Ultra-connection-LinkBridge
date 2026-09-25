---
description: Build and launch the Android app in debug mode
---

```bash
cd android && ./gradlew installDebug && adb shell am start -n com.stayconnect.linkbridge/.app.MainActivity
```
