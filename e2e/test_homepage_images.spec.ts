import { expect } from "@playwright/test"
import { test } from "./fixtures"

test.describe("Homepage images", () => {
  test("homepage loads successfully", async ({ page }) => {
    const response = await page.goto("/image_examples")
    expect(response?.status()).toBe(200)
  })

  test(
    "homepage contains <picture> elements",
    { tag: ["@regression"] },
    async ({ page }) => {
      await page.goto("/image_examples")
      const pictures = page.locator("picture").first()
      await expect(pictures.first()).toBeVisible()
    },
  )

  test("all images inside <picture> elements are loaded", async ({ page }) => {
    await page.goto("/images_examples")
    const images = await page.locator("picture img").all()
    expect(images.length).toBeGreaterThan(0)
    for (const img of images) {
      const naturalWidth = await img.evaluate(
        (el: HTMLImageElement) => el.naturalWidth,
      )
      expect(naturalWidth, "Image should be loaded (naturalWidth > 0)").toBeGreaterThan(0)
    }
  })
})
