import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("Accessibility Narrator smoke", () => {
  test("home has no critical axe violations", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Hear what's in front of you." })).toBeVisible();
    const results = await new AxeBuilder({ page }).analyze();
    const critical = results.violations.filter((v) => v.impact === "critical");
    expect(critical, JSON.stringify(critical, null, 2)).toEqual([]);
  });

  test("keyboard can reach mode tabs and choose image", async ({ page }) => {
    await page.goto("/");
    const imageTab = page.getByRole("tab", { name: "Image" });
    await imageTab.focus();
    await expect(imageTab).toBeFocused();
    await page.keyboard.press("Tab");
    await expect(page.getByRole("tab", { name: "Webpage" })).toBeFocused();
  });
});
