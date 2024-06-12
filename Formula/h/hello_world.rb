class HelloWorld < Formula
  desc "Simple program that outputs 'Hello, World!'"
  homepage "https://app.lizardbyte.dev"
  url "https://github.com/LizardByte/homebrew-release-action.git"
  version "0.0.1"

  def install
    # create hello world sh file with echo command
    (buildpath/"hello-world").write <<~EOS
      #!/bin/sh
      echo "Hello, World!"
    EOS

    # install the hello-world file to the bin directory
    bin.install "hello-world"
  end

  test do
    system "#{bin}/hello-world"
  end
end
# Created from LizardByte/homebrew-release-action@3d4eda009ed3d7d64bf20182d726f6f5b00e7c2b
