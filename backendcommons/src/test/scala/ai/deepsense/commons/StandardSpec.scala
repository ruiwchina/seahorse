/**
 * Copyright 2015 deepsense.ai (CodiLime, Inc)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package ai.deepsense.commons

import scala.concurrent.duration._

import org.scalatest.concurrent.ScalaFutures
import org.scalatest.{Matchers, WordSpec}
import spray.testkit.ScalatestRouteTest

/**
 * Standard base class for tests.  Includes the following features:
 *
 *   - WordSpec style tests with Matcher DSL for assertions
 *
 *   - Support for testing Futures including the useful whenReady construct
 *
 *   - Support for testing spray Routes
 */
class StandardSpec
  extends WordSpec
  with Matchers
  with ScalaFutures
  with ScalatestRouteTest {
  protected implicit def routeTestTimeout: StandardSpec.this.type#RouteTestTimeout = {
    RouteTestTimeout(1.second)
  }
}

