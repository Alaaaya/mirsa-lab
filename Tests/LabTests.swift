import XCTest
final class LabTests: XCTestCase {
 func testTweakUI() throws {
  continueAfterFailure = false
  let app = XCUIApplication()
  app.launch()
  XCTAssertTrue(app.wait(for: .runningForeground, timeout: 20))
  let url = Bundle(for: Self.self).url(forResource: "checks", withExtension: "json")!
  let c = try JSONSerialization.jsonObject(with: Data(contentsOf: url)) as! [String:String]
  func element(_ id: String) -> XCUIElement { app.descendants(matching: .any).matching(identifier: id).firstMatch }
  func screenshot(_ name: String) {
   let a = XCTAttachment(screenshot: app.screenshot()); a.name=name; a.lifetime = .keepAlways; add(a)
  }
  let open = element(c["open"]!); XCTAssertTrue(open.waitForExistence(timeout: 10)); XCTAssertTrue(open.isHittable)
  screenshot("01-injected"); open.tap()
  let panel=element(c["panel"]!); XCTAssertTrue(panel.waitForExistence(timeout: 5)); screenshot("02-menu-open")
  let close=element(c["close"]!); XCTAssertTrue(close.isHittable); close.tap()
  XCTAssertTrue(XCTWaiter.wait(for: [XCTNSPredicateExpectation(predicate: NSPredicate(format: "exists == false"), object: panel)], timeout: 5) == .completed)
  open.tap(); XCTAssertTrue(panel.waitForExistence(timeout: 5)); element(c["close"]!).tap()
  XCTAssertTrue(XCTWaiter.wait(for: [XCTNSPredicateExpectation(predicate: NSPredicate(format: "exists == false"), object: panel)], timeout: 5) == .completed)
  let video=element(c["gesture"]!); XCTAssertTrue(video.isHittable); video.doubleTap()
  let predicate=NSPredicate(format: "value == %@", c["gestureValue"]!)
  expectation(for: predicate, evaluatedWith: video); waitForExpectations(timeout: 5)
  screenshot("03-gesture"); XCTAssertEqual(app.state,.runningForeground)
 }
}
